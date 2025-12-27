"""
Outbox Publisher Service
Processes unpublished events from the outbox table and publishes them to RabbitMQ.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .database import SessionLocal
from .events import rabbitmq_service
from .logger import logger
from .models import OutboxEvent


class OutboxPublisher:
    """
    Background service that processes events from the outbox table.
    Implements the transactional outbox pattern for reliable event publishing.
    """

    def __init__(
        self,
        poll_interval: int = 5,  # seconds between polling
        batch_size: int = 100,  # max events to process per batch
        max_retries: int = 3,  # max retry attempts for failed events
    ):
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the outbox publisher background task."""
        if self.running:
            logger.warning("OutboxPublisher is already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._run())
        logger.info("OutboxPublisher started")

    async def stop(self):
        """Stop the outbox publisher background task."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("OutboxPublisher stopped")

    async def _run(self):
        """Main loop that polls for unpublished events."""
        while self.running:
            try:
                await self._process_batch()
            except Exception as e:
                logger.error(f"Error in OutboxPublisher: {e}", exc_info=True)

            # Wait before next poll
            await asyncio.sleep(self.poll_interval)

    async def _process_batch(self):
        """Process a batch of unpublished events."""
        db: Session = SessionLocal()
        try:
            # Fetch unpublished events
            events = (
                db.query(OutboxEvent)
                .filter(
                    and_(
                        not OutboxEvent.published,
                        OutboxEvent.retry_count < self.max_retries,
                    )
                )
                .order_by(OutboxEvent.created_at)
                .limit(self.batch_size)
                .all()
            )

            if not events:
                return

            logger.info(f"Processing {len(events)} outbox events")

            for event in events:
                try:
                    await self._publish_event(event)

                    # Mark as published
                    event.published = True
                    event.published_at = datetime.now(timezone.utc)
                    db.commit()

                    logger.info(
                        f"Published event {event.event_type} for {event.aggregate_type}:{event.aggregate_id}"
                    )

                except Exception as e:
                    # Increment retry count and log error
                    event.retry_count += 1
                    event.last_error = str(e)
                    db.commit()

                    logger.error(
                        f"Failed to publish event {event.id} (attempt {event.retry_count}/{self.max_retries}): {e}"
                    )

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing outbox batch: {e}", exc_info=True)
        finally:
            db.close()

    async def _publish_event(self, event: OutboxEvent):
        """Publish a single event to RabbitMQ."""
        # Ensure RabbitMQ connection
        await rabbitmq_service.connect()

        # Publish the event
        await rabbitmq_service.publish_event(
            event_name=event.event_type,
            data=event.payload,
        )

    def create_event(
        self,
        db: Session,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict,
    ) -> OutboxEvent:
        """
        Create a new outbox event (to be called from route handlers).

        Args:
            db: Database session
            event_type: Event type/routing key (e.g., 'nucleo.created')
            aggregate_type: Type of aggregate (e.g., 'nucleo', 'course')
            aggregate_id: ID of the aggregate
            payload: Event payload data

        Returns:
            Created OutboxEvent
        """
        event = OutboxEvent(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
            published=False,
            retry_count=0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(event)
        # Note: Caller should commit the transaction
        return event


# Singleton instance
outbox_publisher = OutboxPublisher()
