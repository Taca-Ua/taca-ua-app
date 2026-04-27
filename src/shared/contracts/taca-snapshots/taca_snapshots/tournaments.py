"""
Snapshot DTOs for the Tournaments service.

These models define the typed contract for snapshot data produced by the
Tournaments service and consumed by the Read Model Updater during a rebuild.

Field names mirror the JSON keys currently returned by
``GET /internal/snapshot`` in the tournaments-service.
"""

from datetime import datetime
from typing import List, Optional

from .base import SnapshotBase

# ---------------------------------------------------------------------------
# Individual item snapshots
# ---------------------------------------------------------------------------


class TournamentSnapshotItem(SnapshotBase):
    """A single tournament record."""

    id: str
    modality_id: str
    name: str
    season_id: Optional[str] = None
    scoring_format_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    finished_by: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "modality_id": self.modality_id,
            "name": self.name,
            "scoring_format_id": self.scoring_format_id,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "finished_by": self.finished_by,
        }


class TournamentCompetitorSnapshotItem(SnapshotBase):
    """A single tournament-competitor record."""

    id: str
    tournament_id: str
    competitor_type: Optional[str] = None
    team_id: Optional[str] = None
    athlete_id: Optional[str] = None
    created_at: Optional[datetime] = None
    competitor_course_id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "competitor_type": self.competitor_type,
            "team_id": self.team_id,
            "athlete_id": self.athlete_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "competitor_course_id": self.competitor_course_id,
        }


class TournamentRankingPositionSnapshotItem(SnapshotBase):
    """A single tournament ranking-position record."""

    id: str
    tournament_id: str
    competitor_id: str
    position: int
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "competitor_id": self.competitor_id,
            "position": self.position,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Aggregate snapshot response (full HTTP response body)
# ---------------------------------------------------------------------------


class TournamentsSnapshotResponse(SnapshotBase):
    """
    Full snapshot response returned by ``GET /internal/snapshot`` in the
    tournaments-service.

    This model is used by:
    - **Providers**: returned (or serialised) by the FastAPI endpoint.
    - **Consumers**: parsed from the raw JSON by the snapshot client.
    """

    tournaments: List[TournamentSnapshotItem] = []
    competitors: List[TournamentCompetitorSnapshotItem] = []
    ranking_positions: List[TournamentRankingPositionSnapshotItem] = []
