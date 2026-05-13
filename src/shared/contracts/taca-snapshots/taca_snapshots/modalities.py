"""
Snapshot DTOs for the Modalities service.

These models define the typed contract for snapshot data produced by the
Modalities service and consumed by the Read Model Updater during a rebuild.

Field names mirror the JSON keys currently returned by
``GET /internal/snapshot`` in the modalities-service.
"""

from dataclasses import field
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
    logo_url: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "abbreviation": self.abbreviation,
            "logo_url": self.logo_url,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CourseSnapshotItem(SnapshotBase):
    """A single course record."""

    id: str
    name: str
    abbreviation: str
    nucleo_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "abbreviation": self.abbreviation,
            "nucleo_id": self.nucleo_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ModalityTypeSnapshotItem(SnapshotBase):
    """A single modality-type record."""

    class EscaloType(SnapshotBase):
        name: str
        min_participants: Optional[int] = None
        max_participants: Optional[int] = None
        points: Optional[List[int]] = None

        def to_dict(self) -> dict:
            return {
                "name": self.name,
                "min_participants": self.min_participants,
                "max_participants": self.max_participants,
                "points": self.points,
            }

    id: str
    name: str
    description: Optional[str] = None
    escaloes: Optional[List[EscaloType]] = None
    season_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "escaloes": [e.to_dict() for e in self.escaloes] if self.escaloes else None,
            "season_id": self.season_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ModalitySnapshotItem(SnapshotBase):
    """A single modality record."""

    id: str
    name: Optional[str] = None
    modality_type_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "modality_type_id": self.modality_type_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


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

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "course_id": self.course_id,
            "student_number": self.student_number,
            "is_member": self.is_member,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StaffSnapshotItem(SnapshotBase):
    """A single staff-member record."""

    id: str
    full_name: str
    staff_number: Optional[str] = None
    contact: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "staff_number": self.staff_number,
            "contact": self.contact,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TeamSnapshotItem(SnapshotBase):
    """A single team record."""

    id: str
    modality_id: str
    course_id: str
    name: str
    players: List[str] = field(default_factory=list)  # List of student IDs
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "modality_id": self.modality_id,
            "course_id": self.course_id,
            "name": self.name,
            "players": self.players,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TeamPlayerSnapshotItem(SnapshotBase):
    """A single team–player relationship record."""

    team_id: str
    student_id: str


class RegulationSnapshotItem(SnapshotBase):
    """A single regulation record."""

    id: str
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_url": self.file_url,
        }


class SeasonSnapshotItem(SnapshotBase):
    """A single season record."""

    id: int
    name: str
    created_by: Optional[str] = None
    finished_by: Optional[str] = None
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to a plain dict for JSON serialisation."""
        return {
            "id": self.id,
            "name": self.name,
            "created_by": self.created_by,
            "finished_by": self.finished_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


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
    regulations: List[RegulationSnapshotItem] = []
    seasons: List[SeasonSnapshotItem] = []
