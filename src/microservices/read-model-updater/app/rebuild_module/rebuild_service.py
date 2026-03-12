"""
Read-Model-Updater rebuild service.

Implements :class:`ReadModelRebuildService` — a concrete
:class:`BaseRebuildService` subclass that repopulates all read-model projection
tables from upstream domain service snapshots.

The heavy lifting (clearing tables, inserting rows in FK-safe order) is
delegated to :class:`.projection_repository.ProjectionRepository` so the
orchestration logic stays here and the storage logic stays there.
"""

from typing import Dict, Optional

from taca_rebuild import BaseRebuildService
from taca_snapshots.matches import MatchesSnapshotResponse
from taca_snapshots.modalities import ModalitiesSnapshotResponse
from taca_snapshots.tournaments import TournamentsSnapshotResponse

from ..config import Config
from ..logger import logger
from .dto import (
    CompleteSnapshot,
    MatchesSnapshot,
    ModalitiesSnapshot,
    TournamentSnapshot,
)
from .projection_repository import ProjectionRepository


class ReadModelRebuildService(BaseRebuildService):
    """
    Concrete rebuild service for the read-model-updater.

    To add a new upstream snapshot source:
    1. Add an entry to :attr:`snapshot_sources`.
    2. Handle the new key inside :meth:`rebuild_from_snapshots`.
    """

    def __init__(self, db_session, rabbitmq_svc, timeout=30, max_retries=3):
        super().__init__(
            db_session, rabbitmq_svc, timeout=timeout, max_retries=max_retries
        )
        if db_session is not None:
            self.projection_repo = ProjectionRepository(db_session)

    # ------------------------------------------------------------------
    # Snapshot sources
    # ------------------------------------------------------------------

    @property
    def snapshot_sources(self) -> Dict[str, str]:
        return {
            "matches": f"{Config.MATCHES_SERVICE_URL}/internal/snapshot",
            "tournament": f"{Config.TOURNAMENT_SERVICE_URL}/internal/snapshot",
            "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot",
        }

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------

    def clear_tables(self) -> None:
        logger.info("projections_clearing")
        self.projection_repo.clear_all_projections()
        logger.info("projections_cleared")

    # ------------------------------------------------------------------
    # Rebuild
    # ------------------------------------------------------------------

    def rebuild_from_snapshots(self, raw: Dict[str, Optional[dict]]) -> int:
        matches_raw = raw.get("matches")
        tour_raw = raw.get("tournament")
        mod_raw = raw.get("modalities")

        matches = (
            MatchesSnapshot.from_response(MatchesSnapshotResponse(**matches_raw))
            if matches_raw
            else None
        )
        tournament = (
            TournamentSnapshot.from_response(TournamentsSnapshotResponse(**tour_raw))
            if tour_raw
            else None
        )
        modalities = (
            ModalitiesSnapshot.from_response(ModalitiesSnapshotResponse(**mod_raw))
            if mod_raw
            else None
        )

        snapshot = CompleteSnapshot(
            matches=matches,
            tournament=tournament,
            modalities=modalities,
        )

        logger.info("projections_rebuilding")
        records = self.projection_repo.rebuild_from_snapshot(snapshot)
        self.projection_repo.reset_sequences()
        logger.info("projections_rebuilt", records_processed=records)
        return records

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        try:
            from ..models import (
                Match,
                MatchDetailView,
                Modality,
                Student,
                StudentDetailView,
                Team,
                TeamDetailView,
                Tournament,
                TournamentDetailView,
                TournamentStandingsView,
            )

            return {
                "core_projections": {
                    "matches": self.db.query(Match).count(),
                    "tournaments": self.db.query(Tournament).count(),
                    "teams": self.db.query(Team).count(),
                    "students": self.db.query(Student).count(),
                    "modalities": self.db.query(Modality).count(),
                },
                "materialized_views": {
                    "team_details": self.db.query(TeamDetailView).count(),
                    "student_details": self.db.query(StudentDetailView).count(),
                    "tournament_details": self.db.query(TournamentDetailView).count(),
                    "match_details": self.db.query(MatchDetailView).count(),
                    "tournament_standings": self.db.query(
                        TournamentStandingsView
                    ).count(),
                },
                "event_consumption_paused": getattr(
                    self.rabbitmq_svc, "is_paused", lambda: False
                )(),
            }
        except Exception as exc:
            logger.error("rebuild_status_check_failed", error=str(exc))
            return {"error": "Failed to retrieve status", "message": str(exc)}
