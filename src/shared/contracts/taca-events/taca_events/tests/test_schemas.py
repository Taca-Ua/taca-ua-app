"""
Tests for event schema validation.
"""

import pytest
from taca_events import EventType, validate_event_data


class TestMatchSchemas:
    """Test match event schemas."""

    def test_match_created_valid(self):
        """Test valid match.created event."""
        data = {
            "match_id": "550e8400-e29b-41d4-a716-446655440000",
            "tournament_id": "550e8400-e29b-41d4-a716-446655440001",
            "team_home_id": "550e8400-e29b-41d4-a716-446655440002",
            "team_away_id": "550e8400-e29b-41d4-a716-446655440003",
            "start_time": "2026-01-21T18:00:00Z",
            "created_at": "2026-01-21T12:00:00Z",
        }

        is_valid, errors = validate_event_data(EventType.MATCH_CREATED, data)
        assert is_valid, f"Validation failed: {errors}"

    def test_match_created_missing_required(self):
        """Test match.created with missing required field."""
        data = {
            "match_id": "550e8400-e29b-41d4-a716-446655440000",
            # Missing tournament_id
            "team_home_id": "550e8400-e29b-41d4-a716-446655440002",
            "team_away_id": "550e8400-e29b-41d4-a716-446655440003",
            "start_time": "2026-01-21T18:00:00Z",
            "created_at": "2026-01-21T12:00:00Z",
        }

        is_valid, errors = validate_event_data(EventType.MATCH_CREATED, data)
        assert not is_valid
        assert any("tournament_id" in err for err in errors)


class TestTournamentSchemas:
    """Test tournament event schemas."""

    def test_tournament_created_valid(self):
        """Test valid tournament.created event."""
        data = {
            "tournament_id": "550e8400-e29b-41d4-a716-446655440000",
            "modality_id": "550e8400-e29b-41d4-a716-446655440001",
            "season_id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "Spring Championship 2026",
            "created_at": "2026-01-21T12:00:00Z",
        }

        is_valid, errors = validate_event_data(EventType.TOURNAMENT_CREATED, data)
        assert is_valid, f"Validation failed: {errors}"

    def test_tournament_finished_valid(self):
        """Test valid tournament.finished event."""
        data = {
            "tournament_id": "550e8400-e29b-41d4-a716-446655440000",
            "modality_id": "550e8400-e29b-41d4-a716-446655440001",
            "season_id": "550e8400-e29b-41d4-a716-446655440002",
            "finished_at": "2026-03-21T20:00:00Z",
            "winner_team_id": "550e8400-e29b-41d4-a716-446655440003",
        }

        is_valid, errors = validate_event_data(EventType.TOURNAMENT_FINISHED, data)
        assert is_valid, f"Validation failed: {errors}"


class TestModalitiesSchemas:
    """Test modalities service event schemas."""

    def test_team_created_valid(self):
        """Test valid team.created event."""
        data = {
            "team_id": "550e8400-e29b-41d4-a716-446655440000",
            "modality_id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Computer Science FC",
            "created_at": "2026-01-21T12:00:00Z",
        }

        is_valid, errors = validate_event_data(EventType.TEAM_CREATED, data)
        assert is_valid, f"Validation failed: {errors}"

    def test_student_created_valid(self):
        """Test valid student.created event."""
        data = {
            "student_id": "550e8400-e29b-41d4-a716-446655440000",
            "course_id": "550e8400-e29b-41d4-a716-446655440001",
            "student_number": "202012345",
            "full_name": "João Silva",
            "is_member": True,
            "created_at": "2026-01-21T12:00:00Z",
        }

        is_valid, errors = validate_event_data(EventType.STUDENT_CREATED, data)
        assert is_valid, f"Validation failed: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
