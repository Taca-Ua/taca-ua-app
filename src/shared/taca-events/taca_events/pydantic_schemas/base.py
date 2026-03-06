"""
Pydantic-based EventSchema base class for typed event definitions.

Provides the foundation for all typed event schemas in the TACA system.
Consumers receive the inner ``data`` dict from RabbitMQ handlers; schemas
wrap that payload into strongly-typed objects so handlers can use attribute
access instead of dict lookups.
"""

from typing import Any, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T", bound="EventSchema")


class EventSchema(BaseModel):
    """
    Base class for all typed event schemas.

    Each subclass pairs a typed ``data`` payload with class-level metadata
    (event_type, version, aggregate_type).  Subclasses must define:

    * a ``data`` field typed to a concrete Pydantic model
    * ``event_type()`` classmethod returning the full event-type string
      (e.g. ``'match.created.v1'``)
    * optionally override ``version()`` and ``aggregate_type()``

    Publishing example::

        event = MatchCreatedV1.create(
            aggregate_id=match.id,
            data=MatchCreatedData(match_id=match.id, ...),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="match",
            aggregate_id=match.id,
            data=event.to_data_dict(),
        )

    Consuming example::

        @rabbitmq_service.event_handler(RoutingKeys.MATCH_CREATED)
        def handle_match_created(raw_event: dict):
            event = MatchCreatedV1.from_data(raw_event)
            match_id = event.data.match_id
    """

    data: Any  # Overridden by concrete subclasses

    # ------------------------------------------------------------------ #
    # Class-level metadata (override in subclasses)
    # ------------------------------------------------------------------ #

    @classmethod
    def event_type(cls) -> str:
        """Full event-type string, e.g. ``'match.created.v1'``."""
        raise NotImplementedError(f"{cls.__name__} must implement event_type()")

    @classmethod
    def routing_key(cls) -> str:
        """RabbitMQ routing key (without version suffix)."""
        from taca_events.types import EventType

        return EventType.get_routing_key(cls.event_type())

    @classmethod
    def version(cls) -> str:
        """Semantic version of this event schema, e.g. ``'1.0.0'``."""
        return "1.0.0"

    @classmethod
    def aggregate_type(cls) -> str:
        """Aggregate type derived from event_type, e.g. ``'match'``."""
        return cls.event_type().split(".")[0]

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def create(
        cls: Type[T],
        aggregate_id: UUID,
        data: BaseModel,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> T:
        """
        Create a typed event instance for publishing.

        Args:
            aggregate_id: UUID of the aggregate root.
            data: Typed data payload (concrete Pydantic model).
            correlation_id: Optional correlation identifier.
            causation_id: Optional ID of the causing event.

        Returns:
            A typed ``EventSchema`` subclass instance.
        """
        return cls(data=data)

    @classmethod
    def from_data(cls: Type[T], raw_data: dict) -> T:
        """
        Parse a raw inner-data dict (as received by a RabbitMQ handler)
        into a typed ``EventSchema`` instance.

        The registry calls this during ``EventRegistry.parse()``.

        Args:
            raw_data: The ``data`` payload extracted from the event envelope.

        Returns:
            Typed event schema instance with ``event.data.<field>`` access.
        """
        data_field = cls.model_fields.get("data")
        if data_field is None:
            raise ValueError(f"{cls.__name__} has no 'data' field defined")

        data_cls: Type[BaseModel] = data_field.annotation
        typed_data = data_cls.model_validate(raw_data)
        return cls(data=typed_data)

    # ------------------------------------------------------------------ #
    # Schema evolution
    # ------------------------------------------------------------------ #

    @classmethod
    def upgrade(cls, raw_event: dict) -> dict:
        """
        Upgrade an older raw event dict to the current schema version.

        Override in subclasses to implement schema migration logic.
        The ``EventRegistry`` calls this before validation when a version
        mismatch is detected.

        Args:
            raw_event: Raw event dict (inner data payload).

        Returns:
            Upgraded event dict compatible with the current schema.
        """
        return raw_event

    # ------------------------------------------------------------------ #
    # Serialisation helpers
    # ------------------------------------------------------------------ #

    def to_data_dict(self) -> dict:
        """
        Return the typed ``data`` payload as a JSON-serialisable dict.

        Use this when passing event data to ``outbox_publisher.emit_event()``.
        """
        return self.data.model_dump(mode="json")
