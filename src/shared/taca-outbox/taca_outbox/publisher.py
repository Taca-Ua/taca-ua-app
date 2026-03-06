"""
Shared OutboxPublisher
======================
Background service that polls the outbox table and publishes events to RabbitMQ.

Each microservice wires this up with its own service-specific dependencies
(ORM model, session factory, RabbitMQ service, logger).

Usage::

    from taca_outbox import OutboxPublisher
    from .models import OutboxEvent
    from .database import SessionLocal
    from .events import rabbitmq_service
    from .logger import logger

    outbox_publisher = OutboxPublisher(
        outbox_model=OutboxEvent,
        session_factory=SessionLocal,
        rabbitmq_service=rabbitmq_service,
        logger=logger,
    )

    # In lifespan / startup:
    await outbox_publisher.start()

    # In lifespan / shutdown:
    await outbox_publisher.stop()

    # Inside a request handler (same transaction as the business operation):
    outbox_publisher.emit_event(
        db=session,
        event_type=EventType.SOME_EVENT,
        aggregate_type="entity",
        aggregate_id=entity.id,
        data={...},
    )
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Type
from uuid import UUID


class OutboxPublisher:
    """
    Generic background service that processes events from an outbox table.

    Implements the Transactional Outbox Pattern:
    1. Events are written to the database in the same transaction as the
       business operation (via ``create_event``).
    2. A background loop polls for unpublished events and publishes them
       to RabbitMQ, then marks them as published.
    3. Failed events are retried up to ``max_retries`` times with the
       error recorded in ``last_error``.
    """

    def __init__(
        self,
        outbox_model: Type,
        session_factory: Callable,
        rabbitmq_service: Any,
        logger: Any,
        poll_interval: int = 5,
        batch_size: int = 100,
        max_retries: int = 3,
        service_name: str = "",
    ):
        """
        Parameters
        ----------
        outbox_model:
            The OutboxEvent ORM class created by ``create_outbox_model``.
        session_factory:
            Callable that returns a new SQLAlchemy ``Session`` (e.g.
            ``SessionLocal``).
        rabbitmq_service:
            Service object that exposes ``connect()`` and
            ``publish_event(event_name, data)`` coroutines.
        logger:
            Structured logger (structlog or stdlib).
        poll_interval:
            Seconds between polling rounds.
        batch_size:
            Maximum number of events processed per round.
        max_retries:
            Maximum retry attempts before an event is abandoned.
        service_name:
            Name of the owning service, used as ``published_by`` default in
            ``emit_event`` when no metadata is supplied by the caller.
        """
        self.OutboxEvent = outbox_model
        self.session_factory = session_factory
        self.rabbitmq_service = rabbitmq_service
        self.logger = logger
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.service_name = service_name
        self.running = False
        self._task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the background polling task."""
        if self.running:
            self.logger.warning("OutboxPublisher is already running")
            return
        self.running = True
        self._task = asyncio.create_task(self._run())
        self.logger.info("OutboxPublisher started")

    async def stop(self) -> None:
        """Stop the background polling task gracefully."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("OutboxPublisher stopped")

    # ------------------------------------------------------------------
    # Background loop
    # ------------------------------------------------------------------

    async def _run(self) -> None:
        """Main polling loop."""
        while self.running:
            try:
                await self._process_batch()
            except Exception as exc:
                self.logger.error(f"Error in OutboxPublisher: {exc}", exc_info=True)
            await asyncio.sleep(self.poll_interval)

    async def _process_batch(self) -> None:
        """Fetch and publish one batch of unpublished events."""
        from sqlalchemy import and_

        db = self.session_factory()
        OutboxEvent = self.OutboxEvent
        try:
            events = (
                db.query(OutboxEvent)
                .filter(
                    and_(
                        OutboxEvent.published == False,  # noqa: E712
                        OutboxEvent.retry_count < self.max_retries,
                    )
                )
                .order_by(OutboxEvent.created_at)
                .limit(self.batch_size)
                .all()
            )

            if not events:
                return

            self.logger.info(f"Processing {len(events)} outbox events")

            for event in events:
                try:
                    await self._publish_event(event)

                    event.published = True
                    event.published_at = datetime.now(timezone.utc)
                    db.commit()

                    self.logger.info(
                        f"Published event {event.event_type} for "
                        f"{event.aggregate_type}:{event.aggregate_id}"
                    )

                except Exception as exc:
                    event.retry_count += 1
                    event.last_error = str(exc)
                    db.commit()

                    self.logger.error(
                        f"Failed to publish event {event.id} "
                        f"(attempt {event.retry_count}/{self.max_retries}): {exc}"
                    )

        except Exception as exc:
            db.rollback()
            self.logger.error(f"Error processing outbox batch: {exc}", exc_info=True)
        finally:
            db.close()

    async def _publish_event(self, event: Any) -> None:
        """Publish a single event to RabbitMQ."""
        await self.rabbitmq_service.connect()

        event_envelope = event.payload

        from taca_events import EventType

        routing_key = EventType.get_routing_key(event.event_type)

        await self.rabbitmq_service.publish_event(
            event_name=routing_key,
            data=event_envelope,
        )

    # ------------------------------------------------------------------
    # Outbox write side
    # ------------------------------------------------------------------

    def create_event(self, db: Any, event_envelope: dict) -> Any:
        """
        Persist a new outbox event inside *db*'s current transaction.

        The caller is responsible for committing (or rolling back) the
        transaction together with the business operation.

        Parameters
        ----------
        db:
            Active SQLAlchemy ``Session``.
        event_envelope:
            Complete event envelope dict produced by ``EventBuilder``.

        Returns
        -------
        The newly created (not yet committed) OutboxEvent instance.
        """
        event = self.OutboxEvent(
            event_type=event_envelope["event_type"],
            aggregate_type=event_envelope["aggregate_type"],
            aggregate_id=event_envelope["aggregate_id"],
            payload=event_envelope,
            published=False,
            retry_count=0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(event)
        return event

    def emit_event(
        self,
        db: Any,
        event_type: str,
        aggregate_type: str,
        aggregate_id: UUID,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Build a validated event envelope with ``EventBuilder`` and persist it
        to the outbox inside *db*'s current transaction.

        This combines ``EventBuilder.create()`` and ``create_event()`` into a
        single call.  The caller is still responsible for committing or rolling
        back the enclosing transaction together with the business operation.

        Parameters
        ----------
        db:
            Active SQLAlchemy ``Session``.
        event_type:
            Full event type string (e.g. ``EventType.TOURNAMENT_CREATED``).
        aggregate_type:
            Domain aggregate name (e.g. ``"tournament"``).
        aggregate_id:
            UUID of the aggregate instance.
        data:
            Domain-specific event payload.
        correlation_id:
            Optional request-level correlation identifier.
        causation_id:
            Optional ID of the event that caused this one.
        metadata:
            Optional extra metadata dict.  When omitted, defaults to
            ``{"published_by": self.service_name}``.

        Returns
        -------
        The newly created (not yet committed) OutboxEvent instance.
        """
        from taca_events import EventBuilder

        resolved_metadata = (
            metadata
            if metadata is not None
            else ({"published_by": self.service_name} if self.service_name else {})
        )

        event_envelope = EventBuilder.create(
            event_type=event_type,
            data=data,
            aggregate_id=str(aggregate_id),
            correlation_id=correlation_id,
            causation_id=causation_id,
            metadata=resolved_metadata,
        ).to_dict()

        return self.create_event(db=db, event_envelope=event_envelope)
