"""
Base event envelope schema.
"""

BASE_EVENT_ENVELOPE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "Event Envelope",
    "description": "Standard envelope for all domain events in the TACA system",
    "required": [
        "event_id",
        "event_type",
        "event_version",
        "timestamp",
        "aggregate_type",
        "aggregate_id",
        "data",
    ],
    "properties": {
        "event_id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique identifier for this event instance",
        },
        "event_type": {
            "type": "string",
            "pattern": "^[a-z_]+\\.[a-z_]+(\\.v\\d+)?$",
            "description": "Type of event (e.g., 'match.created.v1')",
        },
        "event_version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$",
            "description": "Semantic version of the event schema (e.g., '1.0.0')",
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp when event was created",
        },
        "correlation_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID to track related events across service boundaries",
        },
        "causation_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the event that caused this event",
        },
        "aggregate_type": {
            "type": "string",
            "description": "Type of aggregate root (e.g., 'match', 'tournament')",
        },
        "aggregate_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the aggregate instance",
        },
        "data": {"type": "object", "description": "Event-specific payload data"},
        "metadata": {
            "type": "object",
            "description": "Optional metadata about event publishing",
            "properties": {
                "published_by": {
                    "type": "string",
                    "description": "Service that published the event",
                },
                "source": {
                    "type": "string",
                    "description": "Source of the event (e.g., 'api', 'scheduler')",
                },
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "ID of user who triggered the event",
                },
            },
        },
    },
    "additionalProperties": False,
}
