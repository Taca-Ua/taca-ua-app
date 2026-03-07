"""
Schema registry for event validation.
"""

from typing import Optional

from .schemas import ALL_SCHEMAS, BASE_EVENT_ENVELOPE_SCHEMA


class SchemaRegistry:
    """
    Central registry for all event schemas.
    Provides access to schemas for validation and documentation.
    """

    @staticmethod
    def get_schema(event_type: str) -> Optional[dict]:
        """
        Get the JSON schema for a specific event type.

        Args:
            event_type: Full event type (e.g., 'match.created.v1')

        Returns:
            JSON schema dict or None if not found
        """
        return ALL_SCHEMAS.get(event_type)

    @staticmethod
    def get_envelope_schema() -> dict:
        """Get the base event envelope schema."""
        return BASE_EVENT_ENVELOPE_SCHEMA

    @staticmethod
    def list_all_events() -> list[str]:
        """Get list of all registered event types."""
        return sorted(ALL_SCHEMAS.keys())

    @staticmethod
    def get_events_by_aggregate(aggregate_type: str) -> list[str]:
        """
        Get all events for a specific aggregate type.

        Args:
            aggregate_type: Aggregate name (e.g., 'match', 'tournament')

        Returns:
            List of event types for that aggregate
        """
        return [
            event_type
            for event_type in ALL_SCHEMAS.keys()
            if event_type.startswith(f"{aggregate_type}.")
        ]

    @staticmethod
    def get_events_by_service(service_name: str) -> list[str]:
        """
        Get all events published by a service.

        Args:
            service_name: Service name (e.g., 'matches', 'modalities', 'tournaments')

        Returns:
            List of event types for that service
        """
        service_aggregates = {
            "matches": ["match"],
            "modalities": [
                "nucleo",
                "course",
                "modality_type",
                "modality",
                "student",
                "staff",
                "team",
            ],
            "tournaments": ["tournament"],
        }

        aggregates = service_aggregates.get(service_name, [])
        events = []
        for aggregate in aggregates:
            events.extend(SchemaRegistry.get_events_by_aggregate(aggregate))
        return events

    @staticmethod
    def schema_exists(event_type: str) -> bool:
        """Check if a schema exists for the given event type."""
        return event_type in ALL_SCHEMAS

    @staticmethod
    def get_schema_info(event_type: str) -> dict:
        """
        Get metadata about a schema.

        Returns:
            Dict with title, description, required fields, etc.
        """
        schema = ALL_SCHEMAS.get(event_type)
        if not schema:
            return {}

        return {
            "event_type": event_type,
            "title": schema.get("title", ""),
            "description": schema.get("description", ""),
            "required_fields": schema.get("required", []),
            "properties": list(schema.get("properties", {}).keys()),
        }
