"""
Snapshot DTOs for the Matches service.

These models define the typed contract for snapshot data produced by the
Matches service and consumed by the Read Model Updater during a rebuild.

Field names mirror the JSON keys currently returned by
``GET /internal/snapshot`` in the matches-service.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import SnapshotBase

# ---------------------------------------------------------------------------
# Individual item snapshots
# ---------------------------------------------------------------------------


class MatchSnapshotItem(SnapshotBase):
    """A single match record as serialised by the snapshot endpoint."""

    match_id: str
    tournament_id: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchSnapshotItem to dict for JSON serialization."""
        return {
            "match_id": self.match_id,
            "tournament_id": self.tournament_id,
            "location": self.location,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }


class MatchParticipantSnapshotItem(SnapshotBase):
    """A single match-participant record as serialised by the snapshot endpoint."""

    participant_id: str
    match_id: str
    participant_type: Optional[str] = None
    participant_entity_id: Optional[str] = None
    added_at: Optional[datetime] = None
    removed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchParticipantSnapshotItem to dict for JSON serialization."""
        return {
            "participant_id": self.participant_id,
            "match_id": self.match_id,
            "participant_type": self.participant_type,
            "participant_entity_id": self.participant_entity_id,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "removed_at": self.removed_at.isoformat() if self.removed_at else None,
        }


class MatchResultSnapshotItem(SnapshotBase):
    """A single match-result record as serialised by the snapshot endpoint."""

    match_id: str
    participant_id: str
    score: Optional[int] = None
    position: Optional[int] = None
    results_metadata: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchResultSnapshotItem to dict for JSON serialization."""
        return {
            "match_id": self.match_id,
            "participant_id": self.participant_id,
            "score": self.score,
            "position": self.position,
            "results_metadata": self.results_metadata,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MatchLineupSnapshotItem(SnapshotBase):
    """A single lineup entry as serialised by the snapshot endpoint."""

    match_id: str
    team_id: str
    player_id: str
    jersey_number: Optional[int] = None
    is_starter: bool = False
    assigned_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchLineupSnapshotItem to dict for JSON serialization."""
        return {
            "match_id": self.match_id,
            "team_id": self.team_id,
            "player_id": self.player_id,
            "jersey_number": self.jersey_number,
            "is_starter": self.is_starter,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
        }


class MatchCommentSnapshotItem(SnapshotBase):
    """A single match comment as serialised by the snapshot endpoint."""

    comment_id: str
    match_id: str
    message: str
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MatchCommentSnapshotItem to dict for JSON serialization."""
        return {
            "comment_id": self.comment_id,
            "match_id": self.match_id,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }


# ---------------------------------------------------------------------------
# Aggregate snapshot response (full HTTP response body)
# ---------------------------------------------------------------------------


class MatchesSnapshotResponse(SnapshotBase):
    """
    Full snapshot response returned by ``GET /internal/snapshot`` in the
    matches-service.

    This model is used by:
    - **Providers**: returned (or serialised) by the FastAPI endpoint.
    - **Consumers**: parsed from the raw JSON by the snapshot client.
    """

    matches: List[MatchSnapshotItem] = []
    participants: List[MatchParticipantSnapshotItem] = []
    results: List[MatchResultSnapshotItem] = []
    lineups: List[MatchLineupSnapshotItem] = []
    comments: List[MatchCommentSnapshotItem] = []
