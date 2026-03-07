"""
Event type constants and catalog.
"""


class EventType:
    """
    Central catalog of all domain event types in the TACA system.

    Event naming convention: {aggregate}.{action}.v{version}
    """

    # ==================== Modalities Service Events ====================

    # Nucleo events
    NUCLEO_CREATED = "nucleo.created.v1"
    NUCLEO_UPDATED = "nucleo.updated.v1"
    NUCLEO_DELETED = "nucleo.deleted.v1"

    # Course events
    COURSE_CREATED = "course.created.v1"
    COURSE_UPDATED = "course.updated.v1"
    COURSE_DELETED = "course.deleted.v1"

    # Modality Type events
    MODALITY_TYPE_CREATED = "modality_type.created.v1"
    MODALITY_TYPE_UPDATED = "modality_type.updated.v1"
    MODALITY_TYPE_DELETED = "modality_type.deleted.v1"

    # Modality events
    MODALITY_CREATED = "modality.created.v1"
    MODALITY_UPDATED = "modality.updated.v1"
    MODALITY_DELETED = "modality.deleted.v1"

    # Student events
    STUDENT_CREATED = "student.created.v1"
    STUDENT_UPDATED = "student.updated.v1"
    STUDENT_DELETED = "student.deleted.v1"

    # Staff events
    STAFF_CREATED = "staff.created.v1"
    STAFF_UPDATED = "staff.updated.v1"
    STAFF_DELETED = "staff.deleted.v1"

    # Team events
    TEAM_CREATED = "team.created.v1"
    TEAM_UPDATED = "team.updated.v1"
    TEAM_DELETED = "team.deleted.v1"
    TEAM_PLAYER_ADDED = "team.player_added.v1"
    TEAM_PLAYER_REMOVED = "team.player_removed.v1"

    # ==================== Tournaments Service Events ====================

    TOURNAMENT_CREATED = "tournament.created.v1"
    TOURNAMENT_UPDATED = "tournament.updated.v1"
    TOURNAMENT_DELETED = "tournament.deleted.v1"
    TOURNAMENT_FINISHED = "tournament.finished.v1"
    TOURNAMENT_COMPETITOR_ADDED = "tournament.competitor.added.v1"
    TOURNAMENT_COMPETITOR_DELETED = "tournament.competitor.deleted.v1"

    # ==================== Matches Service Events ====================

    # Match lifecycle events
    MATCH_CREATED = "match.created.v1"
    MATCH_UPDATED = "match.updated.v1"
    MATCH_DELETED = "match.deleted.v1"

    # Match participant events
    MATCH_PARTICIPANT_ADDED = "match.participant.added.v1"
    MATCH_PARTICIPANT_REMOVED = "match.participant.removed.v1"

    # Match result events
    MATCH_RESULT_UPDATED = "match.result.updated.v1"

    # Match lineup events
    MATCH_LINEUP_ASSIGNED = "match.lineup.assigned.v1"

    # Match comment events
    MATCH_COMMENT_ADDED = "match.comment.added.v1"
    MATCH_COMMENT_DELETED = "match.comment.deleted.v1"

    @classmethod
    def all_events(cls) -> list[str]:
        """Get list of all event types."""
        return [
            value
            for name, value in vars(cls).items()
            if not name.startswith("_") and isinstance(value, str)
        ]

    @classmethod
    def get_aggregate_type(cls, event_type: str) -> str:
        """
        Extract aggregate type from event type.

        Example: "match.created.v1" -> "match"
        """
        return event_type.split(".")[0]

    @classmethod
    def get_action(cls, event_type: str) -> str:
        """
        Extract action from event type.

        Example: "match.created.v1" -> "created"
        """
        parts = event_type.split(".")
        if len(parts) >= 2:
            return parts[1]
        return ""

    @classmethod
    def get_version(cls, event_type: str) -> str:
        """
        Extract version from event type.

        Example: "match.created.v1" -> "v1"
        """
        parts = event_type.split(".")
        if len(parts) >= 3:
            return parts[-1]
        return "v1"

    @classmethod
    def get_routing_key(cls, event_type: str) -> str:
        """
        Get RabbitMQ routing key (without version suffix).

        Example: "match.created.v1" -> "match.created"
        """
        parts = event_type.split(".")
        if len(parts) >= 3 and parts[-1].startswith("v"):
            return ".".join(parts[:-1])
        return event_type


class RoutingKeys(EventType):
    """
    Central catalog of RabbitMQ routing keys for event publishing and subscription.
    """

    for event_type in EventType.all_events():
        routing_key = EventType.get_routing_key(event_type)
        vars()[routing_key.upper().replace(".", "_")] = routing_key
