from uuid import UUID

from taca_events import EventBuilder
from taca_events.pydantic_schemas import EventSchema

from .models import OutboxEvent


def emit_event(event_type: str, aggregate_type: str, aggregate_id: UUID, data: dict):
    """Emit a new event and save it to the outbox.

    Args:
        event_type (str): The type of the event.
        aggregate_type (str): The type of the aggregate associated with the event.
        aggregate_id (UUID): The unique identifier of the aggregate.
        data (dict): The payload data for the event.

    Returns:
        OutboxEvent: The created OutboxEvent instance.
    """

    payload = EventBuilder.create(
        event_type=event_type,
        data=data,
        aggregate_id=str(aggregate_id),
    ).to_dict()

    entry = OutboxEvent(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=payload,
    )
    entry.save()
    return entry


def emit_schema_event(event: EventSchema, aggregate_id: UUID):
    """Emit a new event based on a Pydantic schema and save it to the outbox.

    Args:
        event (EventSchema): The event schema instance.
        aggregate_id (UUID): The unique identifier of the aggregate.

    Returns:
        OutboxEvent: The created OutboxEvent instance.
    """
    return emit_event(
        event_type=event.event_type(),
        aggregate_type=event.aggregate_type(),
        aggregate_id=aggregate_id,
        data=event.to_data_dict(),
    )
