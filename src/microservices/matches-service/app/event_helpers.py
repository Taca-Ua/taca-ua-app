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
        event_type: Full event type (e.g., 'match.created')
        aggregate_type: Type of aggregate (e.g., 'match')
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
    """Domain event types for the matches service."""

    # Match events
    MATCH_CREATED = "match.created"
    MATCH_UPDATED = "match.updated"
    MATCH_DELETED = "match.deleted"

    # Participant events
    PARTICIPANT_ADDED = "match.participant.added"
    PARTICIPANT_REMOVED = "match.participant.removed"
    RESULT_UPDATED = "match.result.updated"
    RESULTS_UPDATED = "match.results.updated"

    # Lineup events
    LINEUP_ASSIGNED = "match.lineup.assigned"

    # Comment events
    COMMENT_ADDED = "match.comment.added"
    COMMENT_DELETED = "match.comment.deleted"
    MATCH_DELETED = "match.deleted"
