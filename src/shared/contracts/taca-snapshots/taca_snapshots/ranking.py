"""
Snapshot DTOs for the Ranking service.

These models define the typed contract for snapshot data produced by the
Ranking service and consumed by the Read Model Updater during a rebuild.

Field names mirror the JSON keys currently returned by
``GET /internal/snapshot`` in the ranking-service.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import SnapshotBase

# ---------------------------------------------------------------------------
# Individual item snapshots
# ---------------------------------------------------------------------------


class ModalityRankingSnapshotItem(SnapshotBase):
    """A single modality-ranking record."""

    id: str
    modality_id: str
    season_id: str
    course_id: str
    points: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    last_updated: Optional[datetime] = None


class CourseRankingSnapshotItem(SnapshotBase):
    """A single course-ranking record."""

    id: str
    course_id: str
    season_id: str
    total_points: Optional[float] = None
    modality_breakdown: Optional[Dict[str, Any]] = None
    last_updated: Optional[datetime] = None


class GeneralRankingSnapshotItem(SnapshotBase):
    """A single general-ranking record."""

    id: str
    season_id: str
    course_id: str
    position: Optional[int] = None
    total_points: Optional[float] = None
    last_updated: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Aggregate snapshot response (full HTTP response body)
# ---------------------------------------------------------------------------


class RankingSnapshotResponse(SnapshotBase):
    """
    Full snapshot response returned by ``GET /internal/snapshot`` in the
    ranking-service.

    This model is used by:
    - **Providers**: returned (or serialised) by the FastAPI endpoint.
    - **Consumers**: parsed from the raw JSON by the snapshot client.
    """

    modality_rankings: List[ModalityRankingSnapshotItem] = []
    course_rankings: List[CourseRankingSnapshotItem] = []
    general_rankings: List[GeneralRankingSnapshotItem] = []
