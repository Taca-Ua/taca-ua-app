"""
Read-model-updater SSE rebuild controller.

SSE-based version of the rebuild service that streams snapshot data
from upstream services instead of fetching entire snapshots at once.

Exposes the standard internal rebuild endpoints (all require ``X-INTERNAL-TOKEN``):
- POST /internal/rebuild
- GET  /internal/rebuild/status
- POST /internal/rebuild/pause
- POST /internal/rebuild/resume
"""

from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session
from taca_models.models import ModalityRankingView
from taca_rebuild import BaseSSERebuildService, make_sse_rebuild_router
from taca_snapshots import matches as match_snapshots
from taca_snapshots import modalities as modality_snapshots
from taca_snapshots import ranking as ranking_snapshots
from taca_snapshots import tournaments as tournament_snapshots

from .config import Config
from .database import get_db_session
from .events import rabbitmq_service
from .logger import logger
from .models import (
    Course,
    GeneralRankings,
    GeneralRankingView,
    Match,
    MatchComment,
    MatchDetailView,
    MatchLineup,
    MatchParticipant,
    MatchResult,
    Modality,
    ModalityRankings,
    ModalityType,
    Nucleo,
    Regulation,
    Staff,
    Student,
    StudentDetailView,
    Team,
    TeamDetailView,
    TeamPlayer,
    Tournament,
    TournamentCompetitor,
    TournamentDetailView,
    TournamentRanking,
    TournamentStandingsView,
)
from .utils import (
    rebuild_general_ranking_projection,
    rebuild_match_projection,
    rebuild_modality_ranking_projection,
    rebuild_student_projection,
    rebuild_team_projection,
    rebuild_tournament_projection,
    rebuild_tournament_standings,
)


class ReadModelSSERebuildService(BaseSSERebuildService):
    """
    SSE-based rebuild service for the Read Model Updater.

    Streams snapshots from upstream services via Server-Sent Events,
    processing events incrementally as they arrive. This is more memory-
    efficient than the HTTP approach for large datasets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track which services we've received complete events from
        self._service_complete = {}

    @property
    def snapshot_sources(self) -> Dict[str, str]:
        return {
            "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot/stream",
            "tournaments": f"{Config.TOURNAMENT_SERVICE_URL}/internal/snapshot/stream",
            "matches": f"{Config.MATCHES_SERVICE_URL}/internal/snapshot/stream",
            "ranking": f"{Config.RANKING_SERVICE_URL}/internal/snapshot/stream",
        }

    def clear_tables(self) -> None:
        logger.info("projections_clearing")
        # Clear in reverse dependency order to respect foreign keys
        self.db.query(GeneralRankingView).delete()
        self.db.query(ModalityRankingView).delete()
        self.db.query(TournamentStandingsView).delete()
        self.db.query(MatchDetailView).delete()
        self.db.query(TournamentDetailView).delete()
        self.db.query(StudentDetailView).delete()
        self.db.query(TeamDetailView).delete()
        self.db.query(MatchComment).delete()
        self.db.query(MatchLineup).delete()
        self.db.query(MatchResult).delete()
        self.db.query(MatchParticipant).delete()
        self.db.query(Match).delete()
        self.db.query(TournamentCompetitor).delete()
        self.db.query(TournamentRanking).delete()
        self.db.query(Tournament).delete()
        self.db.query(TeamPlayer).delete()
        self.db.query(Team).delete()
        self.db.query(Student).delete()
        self.db.query(Staff).delete()
        self.db.query(Modality).delete()
        self.db.query(ModalityType).delete()
        self.db.query(Course).delete()
        self.db.query(Nucleo).delete()
        self.db.query(GeneralRankings).delete()
        self.db.query(ModalityRankings).delete()
        self.db.query(Regulation).delete()
        self.db.flush()
        logger.info("projections_cleared")

    async def rebuild_from_snapshot_event(self, service_name: str, event: dict) -> int:
        """
        Process snapshot events incrementally as they arrive.

        Event types:
        - metadata: Informational, just log
        - batch: Process items and flush
        - complete: Final commit for this service
        - error: Log and skip
        """
        event_type = event.get("type", "")

        if event_type == "metadata":
            count = event.get("count", 0)
            logger.info(f"{service_name}_snapshot_metadata", count=count)
            return 0

        if event_type == "batch":
            items = event.get("items", [])
            category = event.get("category", "unknown")
            return await self._process_batch(service_name, category, items)

        if event_type == "complete":
            count = event.get("records", 0)
            self._service_complete[service_name] = True
            self.db.commit()
            logger.info(f"{service_name}_snapshot_complete", records=count)
            return 0

        if event_type == "error":
            message = event.get("message", "Unknown error")
            logger.error(f"{service_name}_snapshot_error", message=message)
            return 0

        return 0

    async def _process_batch(
        self, service_name: str, category: str, items: List[dict]
    ) -> int:
        """Process a batch of items based on service and category."""
        if not items:
            return 0

        records = 0

        if service_name == "modalities":
            records = self._process_modalities_batch(category, items)

        elif service_name == "tournaments":
            records = self._process_tournaments_batch(category, items)

        elif service_name == "matches":
            records = self._process_matches_batch(category, items)

        elif service_name == "ranking":
            records = self._process_ranking_batch(category, items)

        if records > 0:
            self.db.flush()

        return records

    def _process_modalities_batch(self, category: str, items: List[dict]) -> int:
        """Process modalities service batch events."""
        count = 0

        if category == "nucleos":
            for item in map(
                lambda x: modality_snapshots.NucleoSnapshotItem(**x), items
            ):
                self.db.add(
                    Nucleo(
                        nucleo_id=item.id,
                        name=item.name,
                        abbreviation=item.abbreviation,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )
                count += 1

        elif category == "courses":
            for item in map(
                lambda x: modality_snapshots.CourseSnapshotItem(**x), items
            ):
                self.db.add(
                    Course(
                        course_id=item.id,
                        nucleo_id=item.nucleo_id,
                        name=item.name,
                        abbreviation=item.abbreviation,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )
                count += 1

        elif category == "modality_types":
            for item in map(
                lambda x: modality_snapshots.ModalityTypeSnapshotItem(**x), items
            ):
                self.db.add(
                    ModalityType(
                        modality_type_id=item.id,
                        name=item.name,
                        description=item.description,
                        escaloes=(
                            [e.to_dict() for e in item.escaloes]
                            if item.escaloes
                            else None
                        ),
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )
                count += 1

        elif category == "modalities":
            for item in map(
                lambda x: modality_snapshots.ModalitySnapshotItem(**x), items
            ):
                self.db.add(
                    Modality(
                        modality_id=item.id,
                        modality_type_id=item.modality_type_id,
                        name=item.name,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )
                count += 1

        elif category == "students":
            for item in map(
                lambda x: modality_snapshots.StudentSnapshotItem(**x), items
            ):
                self.db.add(
                    Student(
                        student_id=item.id,
                        course_id=item.course_id,
                        student_number=item.student_number,
                        full_name=item.full_name,
                        is_member=item.is_member,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )
                count += 1

        elif category == "staff":
            pass  # Staff data is not needed in the read model, so we can skip it

        elif category == "teams":
            for item in map(lambda x: modality_snapshots.TeamSnapshotItem(**x), items):
                self.db.add(
                    Team(
                        team_id=item.id,
                        modality_id=item.modality_id,
                        course_id=item.course_id,
                        name=item.name,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                )
                count += 1

                for player in item.players:
                    self.db.add(
                        TeamPlayer(
                            team_id=item.id,
                            student_id=player,
                        )
                    )
                    count += 1

        elif category == "regulations":
            for item in map(
                lambda x: modality_snapshots.RegulationSnapshotItem(**x), items
            ):
                self.db.add(
                    Regulation(
                        id=item.id,
                        title=item.title,
                        description=item.description,
                        file_url=item.file_url,
                    )
                )
                count += 1

        return count

    def _process_tournaments_batch(self, category: str, items: List[dict]) -> int:
        """Process tournaments service batch events."""
        count = 0

        if category == "tournaments":
            for item in map(
                lambda x: tournament_snapshots.TournamentSnapshotItem(**x), items
            ):
                self.db.add(
                    Tournament(
                        tournament_id=item.id,
                        modality_id=item.modality_id,
                        name=item.name,
                        start_date=item.start_date,
                        status=item.status,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                        finished_at=item.finished_at,
                    )
                )
                count += 1

        elif category == "tournament_competitors":
            for item in map(
                lambda x: tournament_snapshots.TournamentCompetitorSnapshotItem(**x),
                items,
            ):
                self.db.add(
                    TournamentCompetitor(
                        competitor_id=item.id,
                        tournament_id=item.tournament_id,
                        competitor_type=item.competitor_type,
                        competitor_entity_id=item.competitor_entity_id,
                        added_at=item.added_at,
                    )
                )
                count += 1

        elif category == "tournament_rankings":
            for item in map(
                lambda x: tournament_snapshots.TournamentRankingSnapshotItem(**x), items
            ):
                self.db.add(
                    TournamentRanking(
                        tournament_id=item.tournament_id,
                        competitor_id=item.competitor_id,
                        position=item.position,
                        created_at=item.created_at,
                    )
                )
                count += 1

        return count

    def _process_matches_batch(self, category: str, items: List[dict]) -> int:
        """Process matches service batch events."""
        count = 0

        if category == "matches":
            for item in map(lambda x: match_snapshots.MatchSnapshotItem(**x), items):
                self.db.add(
                    Match(
                        match_id=item.match_id,
                        tournament_id=item.tournament_id,
                        location=item.location,
                        status=item.status,
                        start_time=item.start_time,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                        deleted_at=item.deleted_at,
                    )
                )
                count += 1

        elif category == "match_participants":
            for item in map(
                lambda x: match_snapshots.MatchParticipantSnapshotItem(**x), items
            ):
                self.db.add(
                    MatchParticipant(
                        match_id=item.match_id,
                        participant_id=item.participant_id,
                        participant_type=item.participant_type,
                        participant_entity_id=item.participant_entity_id,
                        added_at=item.added_at,
                        removed_at=item.removed_at,
                    )
                )
                count += 1

        elif category == "match_results":
            for item in map(
                lambda x: match_snapshots.MatchResultSnapshotItem(**x), items
            ):
                self.db.add(
                    MatchResult(
                        match_id=item.match_id,
                        participant_id=item.participant_id,
                        score=item.score,
                        position=item.position,
                        results_metadata=item.results_metadata,
                        updated_at=item.updated_at,
                    )
                )
                count += 1

        elif category == "match_lineups":
            for item in map(
                lambda x: match_snapshots.MatchLineupSnapshotItem(**x), items
            ):
                self.db.add(
                    MatchLineup(
                        match_id=item.match_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        jersey_number=item.jersey_number,
                        is_starter=item.is_starter,
                        assigned_at=item.assigned_at,
                    )
                )
                count += 1

        elif category == "match_comments":
            for item in map(
                lambda x: match_snapshots.MatchCommentSnapshotItem(**x), items
            ):
                self.db.add(
                    MatchComment(
                        comment_id=item.comment_id,
                        match_id=item.match_id,
                        message=item.message,
                        created_at=item.created_at,
                        deleted_at=item.deleted_at,
                    )
                )
                count += 1

        return count

    def _process_ranking_batch(self, category: str, items: List[dict]) -> int:
        """Process ranking service batch events."""
        count = 0

        if category == "general_rankings":
            for item in map(
                lambda x: ranking_snapshots.GeneralRankingSnapshotItem(**x), items
            ):
                self.db.add(
                    GeneralRankings(
                        course_id=item.course_id,
                        points=item.points,
                        tournaments_participated=item.tournaments_participated,
                    )
                )
                count += 1

        elif category == "modality_rankings":
            for item in map(
                lambda x: ranking_snapshots.ModalityRankingSnapshotItem(**x), items
            ):
                self.db.add(
                    ModalityRankings(
                        modality_id=item.modality_id,
                        course_id=item.course_id,
                        points=item.points,
                    )
                )
                count += 1

        return count

    def get_status(self) -> dict:
        try:
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


# Note: Materialized views and sequence resets should be handled via a separate
# post-rebuild hook or via an async task, as they need to happen after all
# events have been processed and committed.
async def run_post_rebuild_tasks(db_session: Session) -> int:
    """
    Execute expensive operations after projection rebuild completes.

    This runs materialized view rebuilds and sequence resets.
    """
    total = 0

    teams = (
        db_session.query(Team.team_id).filter(Team.deleted_at.is_(None)).yield_per(100)
    )
    for (team_id,) in teams:
        rebuild_team_projection(db_session, team_id)
        total += 1

    students = (
        db_session.query(Student.student_id)
        .filter(Student.deleted_at.is_(None))
        .yield_per(100)
    )
    for (student_id,) in students:
        rebuild_student_projection(db_session, student_id)
        total += 1

    tournaments = (
        db_session.query(Tournament.tournament_id)
        .filter(Tournament.deleted_at.is_(None))
        .yield_per(100)
    )
    for (tournament_id,) in tournaments:
        rebuild_tournament_projection(db_session, tournament_id)
        total += 1

    matches = (
        db_session.query(Match.match_id)
        .filter(Match.deleted_at.is_(None))
        .yield_per(100)
    )
    for (match_id,) in matches:
        rebuild_match_projection(db_session, match_id)
        total += 1

    for (tournament_id,) in tournaments:
        rebuild_tournament_standings(db_session, tournament_id)
    total += db_session.query(TournamentStandingsView).count()

    rebuild_general_ranking_projection(db_session)
    total += db_session.query(GeneralRankingView).count()

    rebuild_modality_ranking_projection(db_session)
    total += db_session.query(ModalityRankingView).count()

    # Reset sequences
    tables_with_sequences = [
        ("public_read.team_players", "id"),
        ("public_read.match_participants", "id"),
        ("public_read.match_results", "id"),
        ("public_read.match_lineups", "id"),
        ("public_read.mv_tournament_standings", "id"),
        ("public_read.mv_general_ranking", "id"),
        ("public_read.general_rankings", "id"),
        ("public_read.modality_rankings", "id"),
        ("public_read.mv_modality_rankings", "id"),
    ]
    for table_name, id_column in tables_with_sequences:
        db_session.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table_name}', '{id_column}'),"
                f" COALESCE((SELECT MAX({id_column}) FROM {table_name}), 1), true)"
            )
        )
    db_session.commit()

    return total


router = make_sse_rebuild_router(
    service_cls=ReadModelSSERebuildService,
    rabbitmq_svc=rabbitmq_service,
    get_db=get_db_session,
    after_rebuild=run_post_rebuild_tasks,
    internal_token=Config.INTERNAL_API_TOKEN,
    timeout=Config.SNAPSHOT_REQUEST_TIMEOUT,
    max_retries=Config.SNAPSHOT_MAX_RETRIES,
)
