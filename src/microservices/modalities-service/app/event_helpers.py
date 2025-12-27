"""
Event helpers for creating domain events via the outbox pattern.
"""

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.orm import Session

from .outbox_publisher import outbox_publisher


def emit_event(
    db: Session,
    event_type: str,
    aggregate_type: str,
    aggregate_id: UUID,
    data: Dict[str, Any],
    action: str = None,
):
    """
    Emit a domain event by saving it to the outbox table.

    Args:
        db: Database session
        event_type: Full event type (e.g., 'nucleo.created')
        aggregate_type: Type of aggregate (e.g., 'nucleo')
        aggregate_id: ID of the aggregate
        data: Event payload
        action: Optional action suffix (will create event_type as {aggregate_type}.{action})
    """
    if action:
        event_type = f"{aggregate_type}.{action}"

    outbox_publisher.create_event(
        db=db,
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=str(aggregate_id),
        payload=data,
    )


# Event type constants for consistency
class EventTypes:
    """Domain event types for the modalities service."""

    # Nucleo events
    NUCLEO_CREATED = "nucleo.created"
    NUCLEO_UPDATED = "nucleo.updated"
    NUCLEO_DELETED = "nucleo.deleted"

    # Course events
    COURSE_CREATED = "course.created"
    COURSE_UPDATED = "course.updated"
    COURSE_DELETED = "course.deleted"

    # Modality Type events
    MODALITY_TYPE_CREATED = "modality_type.created"
    MODALITY_TYPE_UPDATED = "modality_type.updated"
    MODALITY_TYPE_DELETED = "modality_type.deleted"

    # Modality events
    MODALITY_CREATED = "modality.created"
    MODALITY_UPDATED = "modality.updated"
    MODALITY_DELETED = "modality.deleted"

    # Student events
    STUDENT_CREATED = "student.created"
    STUDENT_UPDATED = "student.updated"
    STUDENT_DELETED = "student.deleted"

    # Staff events
    STAFF_CREATED = "staff.created"
    STAFF_UPDATED = "staff.updated"
    STAFF_DELETED = "staff.deleted"

    # Team events
    TEAM_CREATED = "team.created"
    TEAM_UPDATED = "team.updated"
    TEAM_DELETED = "team.deleted"
    TEAM_PLAYER_ADDED = "team.player_added"
    TEAM_PLAYER_REMOVED = "team.player_removed"
