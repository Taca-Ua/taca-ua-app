"""
Event builder for creating standardized events.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class Event:
    """Represents a domain event with standardized envelope."""

    def __init__(
        self,
        event_id: str,
        event_type: str,
        event_version: str,
        timestamp: str,
        aggregate_type: str,
        aggregate_id: str,
        data: dict,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.event_version = event_version
        self.timestamp = timestamp
        self.aggregate_type = aggregate_type
        self.aggregate_id = aggregate_id
        self.data = data
        self.correlation_id = correlation_id
        self.causation_id = causation_id
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        """Convert event to dictionary format."""
        event_dict = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "event_version": self.event_version,
            "timestamp": self.timestamp,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "data": self.data,
        }

        if self.correlation_id:
            event_dict["correlation_id"] = self.correlation_id

        if self.causation_id:
            event_dict["causation_id"] = self.causation_id

        if self.metadata:
            event_dict["metadata"] = self.metadata

        return event_dict

    def __repr__(self) -> str:
        return (
            f"Event(event_type={self.event_type}, "
            f"aggregate_id={self.aggregate_id}, "
            f"event_id={self.event_id})"
        )


class EventBuilder:
    """
    Builder for creating domain events with standardized envelope.

    Usage:
        event = EventBuilder.create(
            event_type=EventType.MATCH_CREATED,
            data={"match_id": "...", ...},
            correlation_id="req-123",
        )
    """

    @staticmethod
    def create(
        event_type: str,
        data: Dict[str, Any],
        aggregate_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        Create a new event with standardized envelope.

        Args:
            event_type: Full event type (e.g., 'match.created.v1')
            data: Event payload data
            aggregate_id: ID of aggregate (extracted from data if not provided)
            correlation_id: Correlation ID for request tracking
            causation_id: ID of event that caused this event
            metadata: Additional metadata (published_by, source, etc.)

        Returns:
            Event instance

        Raises:
            ValueError: If required fields are missing
        """
        from .types import EventType
        from .validator import validate_event_data

        # Extract aggregate type from event_type
        aggregate_type = EventType.get_aggregate_type(event_type)

        # Extract aggregate_id from data if not provided
        if not aggregate_id:
            aggregate_id = EventBuilder._extract_aggregate_id(data, aggregate_type)

        if not aggregate_id:
            raise ValueError(
                f"Cannot determine aggregate_id for {event_type}. "
                f"Provide it explicitly or include {aggregate_type}_id in data."
            )

        # Validate data against schema
        is_valid, errors = validate_event_data(event_type, data)
        if not is_valid:
            raise ValueError(f"Event data validation failed for {event_type}: {errors}")

        # Extract version from event_type
        version = EventBuilder._extract_version(event_type)

        # Create event
        return Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            event_version=version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            data=data,
            correlation_id=correlation_id,
            causation_id=causation_id,
            metadata=metadata,
        )

    @staticmethod
    def _extract_aggregate_id(data: dict, aggregate_type: str) -> Optional[str]:
        """
        Try to extract aggregate ID from data.

        Looks for patterns like:
        - {aggregate_type}_id
        - id (if data has only one id field)
        """
        # Try {aggregate_type}_id
        key = f"{aggregate_type}_id"
        if key in data:
            return str(data[key])

        # Try just 'id'
        if "id" in data:
            return str(data["id"])

        return None

    @staticmethod
    def _extract_version(event_type: str) -> str:
        """
        Extract semantic version from event type.

        Example: 'match.created.v1' -> '1.0.0'
        """
        parts = event_type.split(".")
        if len(parts) >= 3 and parts[-1].startswith("v"):
            version_num = parts[-1][1:]  # Remove 'v' prefix
            # Convert v1 -> 1.0.0
            return f"{version_num}.0.0"
        return "1.0.0"
