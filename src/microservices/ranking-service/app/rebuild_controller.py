"""
Ranking-service rebuild handler.

Implements :class:`RankingRebuildService` (a :class:`BaseRebuildService` subclass)
and wires up the standard internal rebuild router via :func:`make_rebuild_router`.

To add a new upstream snapshot source, add an entry to
:attr:`RankingRebuildService.snapshot_sources` and handle the new key inside
:meth:`RankingRebuildService.rebuild_from_snapshots`.
"""

from typing import Dict, Optional

from taca_rebuild import BaseRebuildService, make_rebuild_router
from taca_snapshots.modalities import ModalitiesSnapshotResponse
from taca_snapshots.tournaments import TournamentsSnapshotResponse

from .config import Config
from .database import get_db_session
from .events import rabbitmq_service
from .logger import logger
from .models import (
    Course,
    CourseRanking,
    GeneralRanking,
    Modality,
    ModalityRanking,
    ModalityType,
    ModalityTypeEscalao,
    Tournament,
    TournamentCompetitor,
    TournamentResult,
)
from .outbox_publisher import outbox_publisher
from .ranking_processor import compute_all_rankings, emit_ranking_computed_event


class RankingRebuildService(BaseRebuildService):
    """
    Concrete rebuild service for the ranking-service.

    Fetches snapshots from the modalities-service and tournaments-service,
    clears all core ranking tables, repopulates them, then recomputes all
    derived ranking tables.
    """

    # ------------------------------------------------------------------
    # Snapshot sources — one entry per upstream service needed
    # ------------------------------------------------------------------

    @property
    def snapshot_sources(self) -> Dict[str, str]:
        return {
            "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot",
            "tournaments": f"{Config.TOURNAMENTS_SERVICE_URL}/internal/snapshot",
        }

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------

    def clear_tables(self) -> None:
        """
        Delete all rows from the ranking-service core tables.

        Order respects FK dependencies (dependents first):
        TournamentResult → TournamentCompetitor → Tournament →
        ModalityTypeEscalao → Modality → ModalityType → Course
        """
        logger.info("core_tables_clearing")
        try:
            self.db.query(TournamentResult).delete()
            self.db.query(TournamentCompetitor).delete()
            self.db.query(Tournament).delete()
            self.db.query(ModalityTypeEscalao).delete()
            self.db.query(Modality).delete()
            self.db.query(ModalityType).delete()
            self.db.query(Course).delete()
            self.db.commit()
            logger.info("core_tables_cleared")
        except Exception as exc:
            self.db.rollback()
            logger.error("core_tables_clear_failed", error=str(exc))
            raise

    # ------------------------------------------------------------------
    # Rebuild
    # ------------------------------------------------------------------

    def rebuild_from_snapshots(self, raw: Dict[str, Optional[dict]]) -> int:
        """
        Parse raw JSON from upstream services and repopulate core tables.

        Insertion order respects FK dependencies:
        ModalityType → ModalityTypeEscalao + Modality → Course →
        Tournament → TournamentCompetitor → TournamentResult

        After populating core tables, derived ranking tables are recomputed
        via :func:`compute_all_rankings`.
        """
        try:
            total = 0

            mod_raw = raw.get("modalities")
            tour_raw = raw.get("tournaments")

            mod = ModalitiesSnapshotResponse(**mod_raw) if mod_raw else None
            tour = TournamentsSnapshotResponse(**tour_raw) if tour_raw else None
            print(tour_raw)

            if mod:
                total += self._insert_modality_types(mod.modality_types)
                total += self._insert_modalities(mod.modalities)
                total += self._insert_courses(mod.courses)

            if tour:
                total += self._insert_tournaments(tour.tournaments)
                total += self._insert_competitors(tour.competitors)
                total += self._insert_ranking_positions(tour.ranking_positions)

            self.db.commit()
            logger.info("core_tables_rebuilt", total_records=total)

            # Recompute derived rankings from freshly populated core tables
            # and emit the RankingComputedV1 event so the read-model-updater
            # can synchronise its GeneralRankingView projection.
            # Compute for every distinct season present in the data.
            distinct_seasons = self.db.query(Tournament.season_id).distinct().all()
            season_ids = [row[0] for row in distinct_seasons]
            for sid in season_ids:
                compute_all_rankings(self.db, sid)
                emit_ranking_computed_event(self.db, outbox_publisher, sid)
            self.db.commit()
            logger.info("derived_tables_computed", seasons_computed=len(season_ids))

            return total

        except Exception as exc:
            self.db.rollback()
            logger.error("core_tables_rebuild_failed", error=str(exc))
            raise

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        return {
            "core_tables": {
                "modality_types": self.db.query(ModalityType).count(),
                "modality_type_escaloes": self.db.query(ModalityTypeEscalao).count(),
                "modalities": self.db.query(Modality).count(),
                "courses": self.db.query(Course).count(),
                "tournaments": self.db.query(Tournament).count(),
                "tournament_competitors": self.db.query(TournamentCompetitor).count(),
                "tournament_results": self.db.query(TournamentResult).count(),
            },
            "derived_tables": {
                "modality_rankings": self.db.query(ModalityRanking).count(),
                "course_rankings": self.db.query(CourseRanking).count(),
                "general_rankings": self.db.query(GeneralRanking).count(),
            },
            "event_consumption_paused": getattr(
                rabbitmq_service, "is_paused", lambda: False
            )(),
        }

    # ------------------------------------------------------------------
    # Private insertion helpers
    # ------------------------------------------------------------------

    def _insert_modality_types(self, items) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(ModalityType(modality_type_id=item.id))
            for escalao in item.escaloes or []:
                self.db.add(
                    ModalityTypeEscalao(
                        modality_type_id=item.id,
                        min_participants=escalao.min_participants,
                        max_participants=escalao.max_participants,
                        points=escalao.points,
                    )
                )
        self.db.flush()
        escalao_count = sum(len(item.escaloes or []) for item in items)
        return len(items) + escalao_count

    def _insert_modalities(self, items) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                Modality(
                    modality_id=item.id,
                    modality_type_id=item.modality_type_id,
                )
            )
        self.db.flush()
        return len(items)

    def _insert_courses(self, items) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(Course(course_id=item.id))
        self.db.flush()
        return len(items)

    def _insert_tournaments(self, items) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                Tournament(
                    tournament_id=item.id,
                    modality_id=item.modality_id,
                    scoring_format_id=item.scoring_format_id,
                    season_id=item.season_id,
                )
            )
        self.db.flush()
        return len(items)

    def _insert_competitors(self, items) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                TournamentCompetitor(
                    tournament_id=item.tournament_id,
                    competitor_id=item.id,
                    competitor_course_id=item.competitor_course_id,
                )
            )
        self.db.flush()
        return len(items)

    def _insert_ranking_positions(self, items) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                TournamentResult(
                    tournament_id=item.tournament_id,
                    competitor_id=item.competitor_id,
                    position=item.position,
                )
            )
        self.db.flush()
        return len(items)


# ---------------------------------------------------------------------------
# Router — standard 4 endpoints, auth and orchestration handled by the package
# ---------------------------------------------------------------------------

router = make_rebuild_router(
    service_cls=RankingRebuildService,
    rabbitmq_svc=rabbitmq_service,
    get_db=get_db_session,
    internal_token=Config.INTERNAL_API_TOKEN,
    timeout=Config.SNAPSHOT_REQUEST_TIMEOUT,
    max_retries=Config.SNAPSHOT_MAX_RETRIES,
)
