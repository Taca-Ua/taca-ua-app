"""
Snapshot DTOs for the Ranking service.

These models define the typed contract for snapshot data produced by the
Ranking service and consumed by the Read Model Updater during a rebuild.

Field names mirror the JSON keys currently returned by
``GET /internal/snapshot`` in the ranking-service.
"""

from typing import List

from .base import SnapshotBase

# ---------------------------------------------------------------------------
# Individual item snapshots
# ---------------------------------------------------------------------------


class GeneralRankingSnapshotItem(SnapshotBase):
    """Points earned by a single course across all modalities."""

    course_id: str
    points: int
    tournaments_participated: int = 0

    def to_dict(self) -> dict:
        return {
            "course_id": self.course_id,
            "points": self.points,
            "tournaments_participated": self.tournaments_participated,
        }


class ModalityRankingSnapshotItem(SnapshotBase):
    """Points earned by a course within a specific modality."""

    modality_id: str
    course_id: str
    points: int

    def to_dict(self) -> dict:
        return {
            "modality_id": self.modality_id,
            "course_id": self.course_id,
            "points": self.points,
        }


class CourseRankingSnapshotItem(SnapshotBase):
    """Aggregated course ranking with per-modality breakdown."""

    course_id: str
    points: int
    modality_breakdown: List[int] = []

    def to_dict(self) -> dict:
        return {
            "course_id": self.course_id,
            "points": self.points,
            "modality_breakdown": self.modality_breakdown,
        }


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

    general_rankings: List[GeneralRankingSnapshotItem] = []
    modality_rankings: List[ModalityRankingSnapshotItem] = []
    course_rankings: List[CourseRankingSnapshotItem] = []
