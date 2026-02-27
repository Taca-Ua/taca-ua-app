"""
Rebuild Service - Core orchestration logic for projection rebuild.

This service orchestrates the complete rebuild process:
1. Pause event consumption
2. Clear all projections
3. Fetch snapshots from domain services
4. Rebuild projections from snapshots
5. Resume event consumption

Architecture Notes:
- This is the ONLY component that orchestrates rebuild
- API Gateway must NOT orchestrate rebuild
- Domain services must NOT call each other
- Rebuild is triggered manually via internal endpoint
- Event consumption is paused during rebuild to prevent inconsistencies
"""

import time

from sqlalchemy.orm import Session

from ..logger import logger
from .dto import CompleteSnapshot, RebuildResult
from .projection_repository import ProjectionRepository
from .snapshot_client import SnapshotClient, SnapshotFetchError


class RebuildService:
    """
    Service for orchestrating projection rebuild from domain service snapshots.

    This service ensures:
    - Event consumption is paused during rebuild
    - Projections are cleared safely
    - Snapshots are fetched from all domain services
    - Projections are rebuilt in correct order
    - Event consumption resumes after rebuild
    - Idempotency (can be triggered multiple times safely)

    CRITICAL: This service must be the single orchestrator for rebuild.
    No other service should trigger or manage the rebuild process.
    """

    def __init__(self, db_session: Session, rabbitmq_service):
        """
        Initialize rebuild service.

        Args:
            db_session: Database session for projection operations
            rabbitmq_service: RabbitMQ service instance for pause/resume
        """
        self.db_session = db_session
        self.rabbitmq_service = rabbitmq_service
        self.snapshot_client = SnapshotClient()
        self.projection_repo = ProjectionRepository(db_session)

    async def execute_rebuild(self) -> RebuildResult:
        """
        Execute complete rebuild process.

        This is the main entry point for rebuild operations.
        It orchestrates all steps and ensures proper error handling.

        Returns:
            RebuildResult with success status and metadata

        Process:
        1. Pause event consumption
        2. Clear all projection tables
        3. Fetch snapshots from all domain services
        4. Rebuild projections from snapshots
        5. Resume event consumption

        If any step fails, the process attempts to resume event consumption
        before propagating the error.
        """
        start_time = time.time()
        result = RebuildResult(
            success=False,
            message="Rebuild in progress",
            records_processed=0,
            duration_seconds=0.0,
            errors=[],
        )

        logger.info("rebuild_started")

        try:
            # Step 1: Pause event consumption
            # This ensures no new events are processed during rebuild
            logger.info("rebuild_step", step="pause_event_consumption")
            await self.pause_event_consumption()

            # Step 2: Clear all projection tables
            # This removes all existing data to prepare for fresh rebuild
            logger.info("rebuild_step", step="clear_projections")
            self.clear_projections()

            # Step 3: Fetch snapshots from all domain services
            # Uses HTTP to call /internal/snapshot endpoints
            logger.info("rebuild_step", step="fetch_snapshots")
            snapshot = await self.fetch_snapshots()

            # Validate that we have some data to rebuild
            if not snapshot.has_data():
                result.add_error("No snapshot data available from any service")
                logger.warning("rebuild_no_data")
                return result

            # Step 4: Rebuild projections from snapshots
            # Inserts data in correct order respecting foreign keys
            logger.info("rebuild_step", step="rebuild_projections")
            records_processed = self.rebuild_projections(snapshot)

            # Step 5: Resume event consumption
            # Events can now be processed again
            logger.info("rebuild_step", step="resume_event_consumption")
            await self.resume_event_consumption()

            # Calculate duration and finalize result
            duration = time.time() - start_time

            result.success = True
            result.message = "Rebuild completed successfully"
            result.records_processed = records_processed
            result.duration_seconds = duration

            logger.info(
                "rebuild_completed",
                success=True,
                records_processed=records_processed,
                duration_seconds=duration,
            )

            return result

        except SnapshotFetchError as e:
            # Snapshot fetching failed
            error_msg = f"Failed to fetch snapshots: {str(e)}"
            result.add_error(error_msg)
            logger.error(
                "rebuild_failed",
                step="fetch_snapshots",
                error=error_msg,
                service=e.service_name,
            )

            # Attempt to resume event consumption even if rebuild failed
            try:
                await self.resume_event_consumption()
            except Exception as resume_error:
                logger.error(
                    "rebuild_resume_failed_after_error",
                    error=str(resume_error),
                )

            return result

        except Exception as e:
            # Unexpected error during rebuild
            error_msg = f"Unexpected error during rebuild: {str(e)}"
            result.add_error(error_msg)
            logger.error("rebuild_failed", error=error_msg)

            # Attempt to resume event consumption even if rebuild failed
            try:
                await self.resume_event_consumption()
            except Exception as resume_error:
                logger.error(
                    "rebuild_resume_failed_after_error",
                    error=str(resume_error),
                )

            return result

        finally:
            # Always calculate final duration
            result.duration_seconds = time.time() - start_time

    async def pause_event_consumption(self) -> None:
        """
        Pause RabbitMQ event consumption.

        This prevents new events from being processed during rebuild,
        ensuring data consistency.

        The implementation depends on the RabbitMQ service having
        a pause mechanism (to be implemented separately).
        """
        logger.info("event_consumption_pausing")

        # Check if rabbitmq_service has pause method
        if hasattr(self.rabbitmq_service, "pause_consumption"):
            await self.rabbitmq_service.pause_consumption()
            logger.info("event_consumption_paused")
        else:
            # Fallback: Log warning if pause not implemented
            logger.warning(
                "event_consumption_pause_not_implemented",
                message="RabbitMQ service does not support pause. "
                "Events may be processed during rebuild.",
            )

    def clear_projections(self) -> None:
        """
        Clear all projection tables safely.

        Delegates to ProjectionRepository which handles the correct
        deletion order to respect foreign key constraints.
        """
        logger.info("projections_clearing")
        self.projection_repo.clear_all_projections()
        logger.info("projections_cleared")

    async def fetch_snapshots(self) -> CompleteSnapshot:
        """
        Fetch snapshots from all domain services.

        Uses SnapshotClient to make HTTP requests to each service's
        /internal/snapshot endpoint.

        Returns:
            CompleteSnapshot with data from all services

        Raises:
            SnapshotFetchError: If any service fails to provide snapshot
        """
        logger.info("snapshots_fetching")
        snapshot = await self.snapshot_client.fetch_all_snapshots()
        logger.info(
            "snapshots_fetched",
            total_records=snapshot.get_total_record_count(),
        )
        return snapshot

    def rebuild_projections(self, snapshot: CompleteSnapshot) -> int:
        """
        Rebuild all projection tables from snapshot data.

        Delegates to ProjectionRepository which handles the correct
        insertion order to respect foreign key constraints.

        Args:
            snapshot: Complete snapshot data from all services

        Returns:
            Number of records inserted

        Raises:
            Exception: If rebuild fails (database transaction rolled back)
        """
        logger.info("projections_rebuilding")
        records_processed = self.projection_repo.rebuild_from_snapshot(snapshot)

        # Reset sequences to ensure new inserts don't conflict
        self.projection_repo.reset_sequences()

        logger.info("projections_rebuilt", records_processed=records_processed)
        return records_processed

    async def resume_event_consumption(self) -> None:
        """
        Resume RabbitMQ event consumption.

        This allows events to be processed again after rebuild is complete.

        The implementation depends on the RabbitMQ service having
        a resume mechanism (to be implemented separately).
        """
        logger.info("event_consumption_resuming")

        # Check if rabbitmq_service has resume method
        if hasattr(self.rabbitmq_service, "resume_consumption"):
            await self.rabbitmq_service.resume_consumption()
            logger.info("event_consumption_resumed")
        else:
            # Fallback: Log warning if resume not implemented
            logger.warning(
                "event_consumption_resume_not_implemented",
                message="RabbitMQ service does not support resume.",
            )

    def get_rebuild_status(self) -> dict:
        """
        Get current rebuild status.

        This can be used to check if a rebuild is in progress,
        how many records are in projection tables, etc.

        Returns:
            Dictionary with status information
        """
        # Query database for projection counts
        # This is useful for monitoring and debugging

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

            match_count = self.db_session.query(Match).count()
            tournament_count = self.db_session.query(Tournament).count()
            team_count = self.db_session.query(Team).count()
            student_count = self.db_session.query(Student).count()
            modality_count = self.db_session.query(Modality).count()

            # Materialized view counts
            team_detail_count = self.db_session.query(TeamDetailView).count()
            student_detail_count = self.db_session.query(StudentDetailView).count()
            tournament_detail_count = self.db_session.query(
                TournamentDetailView
            ).count()
            match_detail_count = self.db_session.query(MatchDetailView).count()
            standings_count = self.db_session.query(TournamentStandingsView).count()

            return {
                "core_projections": {
                    "matches": match_count,
                    "tournaments": tournament_count,
                    "teams": team_count,
                    "students": student_count,
                    "modalities": modality_count,
                },
                "materialized_views": {
                    "team_details": team_detail_count,
                    "student_details": student_detail_count,
                    "tournament_details": tournament_detail_count,
                    "match_details": match_detail_count,
                    "tournament_standings": standings_count,
                },
                "event_consumption_paused": getattr(
                    self.rabbitmq_service, "is_paused", lambda: False
                )(),
            }

        except Exception as e:
            logger.error("rebuild_status_check_failed", error=str(e))
            return {
                "error": "Failed to retrieve status",
                "message": str(e),
            }
