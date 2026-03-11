"""
Snapshot DTOs for the Modalities service.

These models define the typed contract for snapshot data produced by the
Modalities service and consumed by the Read Model Updater during a rebuild.

Field names mirror the JSON keys currently returned by
``GET /internal/snapshot`` in the modalities-service.
"""

from datetime import datetime
from typing import List, Optional

from .base import SnapshotBase

# ---------------------------------------------------------------------------
# Individual item snapshots
# ---------------------------------------------------------------------------


class NucleoSnapshotItem(SnapshotBase):
    """A single nucleo record."""

    id: str
    name: str
    abbreviation: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CourseSnapshotItem(SnapshotBase):
    """A single course record."""

    id: str
    name: str
    abbreviation: str
    nucleo_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ModalityTypeSnapshotItem(SnapshotBase):
    """A single modality-type record."""

    class EscaloType(SnapshotBase):
        min_participants: Optional[int] = None
        max_participants: Optional[int] = None
        points: Optional[List[int]] = None

    id: str
    name: str
    description: Optional[str] = None
    escaloes: Optional[List[EscaloType]] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ModalitySnapshotItem(SnapshotBase):
    """A single modality record."""

    id: str
    name: Optional[str] = None
    modality_type_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StudentSnapshotItem(SnapshotBase):
    """A single student record."""

    id: str
    full_name: str
    course_id: str
    student_number: Optional[str] = None
    is_member: bool = False
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StaffSnapshotItem(SnapshotBase):
    """A single staff-member record."""

    id: str
    full_name: str
    staff_number: Optional[str] = None
    contact: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TeamSnapshotItem(SnapshotBase):
    """A single team record."""

    id: str
    modality_id: str
    course_id: str
    name: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TeamPlayerSnapshotItem(SnapshotBase):
    """A single team–player relationship record."""

    team_id: str
    student_id: str


# ---------------------------------------------------------------------------
# Aggregate snapshot response (full HTTP response body)
# ---------------------------------------------------------------------------


class ModalitiesSnapshotResponse(SnapshotBase):
    """
    Full snapshot response returned by ``GET /internal/snapshot`` in the
    modalities-service.

    This model is used by:
    - **Providers**: returned (or serialised) by the FastAPI endpoint.
    - **Consumers**: parsed from the raw JSON by the snapshot client.
    """

    nucleos: List[NucleoSnapshotItem] = []
    courses: List[CourseSnapshotItem] = []
    modality_types: List[ModalityTypeSnapshotItem] = []
    modalities: List[ModalitySnapshotItem] = []
    students: List[StudentSnapshotItem] = []
    staff: List[StaffSnapshotItem] = []
    teams: List[TeamSnapshotItem] = []
    team_players: List[TeamPlayerSnapshotItem] = []
