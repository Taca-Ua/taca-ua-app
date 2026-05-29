"""
Background scheduler for automatic match status updates.
Periodically checks scheduled matches and updates status to in_progress when start time has passed.
"""

from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import and_
from taca_events.pydantic_schemas.matches import MatchUpdatedData, MatchUpdatedV1

from .database import SessionLocal
from .logger import logger
from .models import Match, MatchStatus
from .outbox_publisher import outbox_publisher


class MatchStatusScheduler:
    """Manages background scheduler for match status updates."""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None

    async def start(self):
        """Start the scheduler."""
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()

        # Add job: check every 5 minutes
        self.scheduler.add_job(
            self.update_scheduled_matches,
            "interval",
            minutes=5,
            id="update_match_status",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("match_status_scheduler_started", interval_minutes=5)

    async def stop(self):
        """Stop the scheduler."""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("match_status_scheduler_stopped")

    async def update_scheduled_matches(self):
        """
        Query all SCHEDULED matches and update those with start_time in the past
        to IN_PROGRESS status.
        """
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)

            # Find all scheduled matches with start_time <= now
            matches_to_update = (
                db.query(Match)
                .filter(
                    and_(
                        Match.status == MatchStatus.SCHEDULED,
                        Match.start_time <= now,
                    )
                )
                .all()
            )

            if not matches_to_update:
                logger.debug("no_scheduled_matches_to_update")
                return

            logger.info(
                "updating_match_statuses",
                count=len(matches_to_update),
                current_time=now.isoformat(),
            )

            for match in matches_to_update:
                old_status = match.status.value
                match.status = MatchStatus.IN_PROGRESS
                match.updated_at = now

                # Emit event for status change
                event = MatchUpdatedV1.create(
                    aggregate_id=match.id,
                    data=MatchUpdatedData(
                        match_id=match.id,
                        location=None,
                        start_time=None,
                        status=MatchStatus.IN_PROGRESS.value,
                    ),
                )
                outbox_publisher.emit_event(
                    db,
                    event_type=event.event_type(),
                    aggregate_type="match",
                    aggregate_id=match.id,
                    data=event.to_data_dict(),
                )

                logger.info(
                    "match_status_updated",
                    match_id=str(match.id),
                    old_status=old_status,
                    new_status=MatchStatus.IN_PROGRESS.value,
                    start_time=match.start_time.isoformat(),
                )

            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(
                "error_updating_match_statuses",
                error=str(e),
                exc_info=True,
            )
        finally:
            db.close()


# Singleton instance
match_scheduler = MatchStatusScheduler()
