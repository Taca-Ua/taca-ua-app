"""
Event helpers for creating domain events via the outbox pattern.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from taca_events import EventBuilder

from .outbox_publisher import outbox_publisher


def emit_event(
    db: Session,
    event_type: str,
    aggregate_type: str,
    aggregate_id: UUID,
    data: Dict[str, Any],
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Emit a domain event by saving it to the outbox table.
    Uses EventBuilder to create validated events with standardized envelope.

    Args:
        db: Database session
        event_type: Full event type from EventType constants (e.g., EventType.NUCLEO_CREATED)
        aggregate_type: Type of aggregate (e.g., 'nucleo')
        aggregate_id: ID of the aggregate
        data: Event payload
        correlation_id: Optional correlation ID for request tracking
        causation_id: Optional causation ID (event that caused this event)
        metadata: Optional metadata (published_by, source, user_id, etc.)
    """
    # Build and validate event using EventBuilder
    event = EventBuilder.create(
        event_type=event_type,
        data=data,
        aggregate_id=str(aggregate_id),
        correlation_id=correlation_id,
        causation_id=causation_id,
        metadata=metadata or {"published_by": "modalities-service"},
    )

    # Store the complete event envelope in outbox
    outbox_publisher.create_event(
        db=db,
        event_envelope=event.to_dict(),
    )
