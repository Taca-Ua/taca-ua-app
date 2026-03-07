"""
Tests for EventBuilder.
"""

import pytest
from taca_events import EventBuilder, EventType


class TestEventBuilder:
    """Test event builder functionality."""

    def test_create_event_with_explicit_aggregate_id(self):
        """Test creating event with explicit aggregate_id."""
        event = EventBuilder.create(
            event_type=EventType.MATCH_CREATED,
            aggregate_id="550e8400-e29b-41d4-a716-446655440000",
            data={
                "match_id": "550e8400-e29b-41d4-a716-446655440000",
                "tournament_id": "550e8400-e29b-41d4-a716-446655440001",
                "team_home_id": "550e8400-e29b-41d4-a716-446655440002",
                "team_away_id": "550e8400-e29b-41d4-a716-446655440003",
                "start_time": "2026-01-21T18:00:00Z",
                "created_at": "2026-01-21T12:00:00Z",
            },
        )

        assert event.event_type == EventType.MATCH_CREATED
        assert event.aggregate_type == "match"
        assert event.aggregate_id == "550e8400-e29b-41d4-a716-446655440000"
        assert event.event_id is not None

    def test_create_event_extracts_aggregate_id(self):
        """Test that builder extracts aggregate_id from data."""
        event = EventBuilder.create(
            event_type=EventType.MATCH_CREATED,
            data={
                "match_id": "550e8400-e29b-41d4-a716-446655440000",
                "tournament_id": "550e8400-e29b-41d4-a716-446655440001",
                "team_home_id": "550e8400-e29b-41d4-a716-446655440002",
                "team_away_id": "550e8400-e29b-41d4-a716-446655440003",
                "start_time": "2026-01-21T18:00:00Z",
                "created_at": "2026-01-21T12:00:00Z",
            },
        )

        assert event.aggregate_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_create_event_with_correlation_id(self):
        """Test creating event with correlation ID."""
        event = EventBuilder.create(
            event_type=EventType.MATCH_CREATED,
            data={
                "match_id": "550e8400-e29b-41d4-a716-446655440000",
                "tournament_id": "550e8400-e29b-41d4-a716-446655440001",
                "team_home_id": "550e8400-e29b-41d4-a716-446655440002",
                "team_away_id": "550e8400-e29b-41d4-a716-446655440003",
                "start_time": "2026-01-21T18:00:00Z",
                "created_at": "2026-01-21T12:00:00Z",
            },
            correlation_id="req-12345",
        )

        assert event.correlation_id == "req-12345"

    def test_create_event_with_metadata(self):
        """Test creating event with metadata."""
        event = EventBuilder.create(
            event_type=EventType.MATCH_CREATED,
            data={
                "match_id": "550e8400-e29b-41d4-a716-446655440000",
                "tournament_id": "550e8400-e29b-41d4-a716-446655440001",
                "team_home_id": "550e8400-e29b-41d4-a716-446655440002",
                "team_away_id": "550e8400-e29b-41d4-a716-446655440003",
                "start_time": "2026-01-21T18:00:00Z",
                "created_at": "2026-01-21T12:00:00Z",
            },
            metadata={
                "published_by": "matches-service",
                "source": "api",
            },
        )

        assert event.metadata["published_by"] == "matches-service"
        assert event.metadata["source"] == "api"

    def test_create_event_validates_data(self):
        """Test that builder validates data against schema."""
        with pytest.raises(ValueError, match="validation failed"):
            EventBuilder.create(
                event_type=EventType.MATCH_CREATED,
                data={
                    "match_id": "550e8400-e29b-41d4-a716-446655440000",
                    # Missing required fields
                },
            )

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = EventBuilder.create(
            event_type=EventType.MATCH_CREATED,
            data={
                "match_id": "550e8400-e29b-41d4-a716-446655440000",
                "tournament_id": "550e8400-e29b-41d4-a716-446655440001",
                "team_home_id": "550e8400-e29b-41d4-a716-446655440002",
                "team_away_id": "550e8400-e29b-41d4-a716-446655440003",
                "start_time": "2026-01-21T18:00:00Z",
                "created_at": "2026-01-21T12:00:00Z",
            },
            correlation_id="req-12345",
        )

        event_dict = event.to_dict()

        assert event_dict["event_type"] == EventType.MATCH_CREATED
        assert event_dict["aggregate_type"] == "match"
        assert event_dict["correlation_id"] == "req-12345"
        assert "data" in event_dict
        assert event_dict["data"]["match_id"] == "550e8400-e29b-41d4-a716-446655440000"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
