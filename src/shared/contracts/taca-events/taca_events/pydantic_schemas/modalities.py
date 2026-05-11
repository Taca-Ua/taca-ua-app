"""
Typed Pydantic event schemas for the Modalities Service.

Covers: Nucleo, Course, ModalityType, Modality, Student, Staff, Team,
TeamPlayer events.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema

# ================================================================== #
# Nucleo
# ================================================================== #


class NucleoCreatedData(BaseModel):
    nucleo_id: UUID
    name: str
    abbreviation: str
    logo_url: Optional[str] = None


class NucleoUpdatedData(BaseModel):
    nucleo_id: UUID
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    logo_url: Optional[str] = None


class NucleoDeletedData(BaseModel):
    nucleo_id: UUID


class NucleoCreatedV1(EventSchema):
    data: NucleoCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "nucleo.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "nucleo"


class NucleoUpdatedV1(EventSchema):
    data: NucleoUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "nucleo.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "nucleo"


class NucleoDeletedV1(EventSchema):
    data: NucleoDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "nucleo.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "nucleo"


# ================================================================== #
# Course
# ================================================================== #


class CourseCreatedData(BaseModel):
    course_id: UUID
    nucleo_id: UUID
    name: str
    abbreviation: str


class CourseUpdatedData(BaseModel):
    course_id: UUID
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    nucleo_id: Optional[UUID] = None


class CourseDeletedData(BaseModel):
    course_id: UUID


class CourseCreatedV1(EventSchema):
    data: CourseCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "course.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "course"


class CourseUpdatedV1(EventSchema):
    data: CourseUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "course.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "course"


class CourseDeletedV1(EventSchema):
    data: CourseDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "course.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "course"


# ================================================================== #
# ModalityType
# ================================================================== #
class _EscalaoData(BaseModel):
    name: str
    min_participants: Optional[int] = None
    max_participants: Optional[int] = None
    points: list[int]


class ModalityTypeCreatedData(BaseModel):

    modality_type_id: UUID
    season_id: int
    name: str
    description: str
    escaloes: list[_EscalaoData]


class ModalityTypeUpdatedData(BaseModel):
    modality_type_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    escaloes: Optional[list[_EscalaoData]] = None


class ModalityTypeDeletedData(BaseModel):
    modality_type_id: UUID


class ModalityTypeCreatedV1(EventSchema):
    data: ModalityTypeCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "modality_type.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "modality_type"


class ModalityTypeUpdatedV1(EventSchema):
    data: ModalityTypeUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "modality_type.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "modality_type"


class ModalityTypeDeletedV1(EventSchema):
    data: ModalityTypeDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "modality_type.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "modality_type"


# ================================================================== #
# Modality
# ================================================================== #


class ModalityCreatedData(BaseModel):
    modality_id: UUID
    modality_type_id: UUID
    name: Optional[str] = None


class ModalityUpdatedData(BaseModel):
    modality_id: UUID
    name: Optional[str] = None
    modality_type_id: Optional[UUID] = None


class ModalityDeletedData(BaseModel):
    modality_id: UUID


class ModalityCreatedV1(EventSchema):
    data: ModalityCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "modality.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "modality"


class ModalityUpdatedV1(EventSchema):
    data: ModalityUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "modality.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "modality"


class ModalityDeletedV1(EventSchema):
    data: ModalityDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "modality.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "modality"


# ================================================================== #
# Student
# ================================================================== #


class StudentCreatedData(BaseModel):
    student_id: UUID
    full_name: str
    course_id: UUID
    student_number: str
    is_member: bool = False


class StudentUpdatedData(BaseModel):
    student_id: UUID
    full_name: Optional[str] = None
    course_id: Optional[UUID] = None
    student_number: Optional[str] = None
    is_member: Optional[bool] = None


class StudentDeletedData(BaseModel):
    student_id: UUID


class StudentCreatedV1(EventSchema):
    data: StudentCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "student.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "student"


class StudentUpdatedV1(EventSchema):
    data: StudentUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "student.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "student"


class StudentDeletedV1(EventSchema):
    data: StudentDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "student.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "student"


# ================================================================== #
# Staff
# ================================================================== #


class StaffCreatedData(BaseModel):
    staff_id: UUID
    full_name: str
    staff_number: Optional[str] = None
    contact: Optional[str] = None


class StaffUpdatedData(BaseModel):
    staff_id: UUID
    full_name: Optional[str] = None
    staff_number: Optional[str] = None
    contact: Optional[str] = None


class StaffDeletedData(BaseModel):
    staff_id: UUID


class StaffCreatedV1(EventSchema):
    data: StaffCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "staff.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "staff"


class StaffUpdatedV1(EventSchema):
    data: StaffUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "staff.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "staff"


class StaffDeletedV1(EventSchema):
    data: StaffDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "staff.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "staff"


# ================================================================== #
# Team
# ================================================================== #


class TeamCreatedData(BaseModel):
    team_id: UUID
    name: str
    modality_id: UUID
    course_id: UUID


class TeamUpdatedData(BaseModel):
    team_id: UUID
    name: Optional[str] = None
    modality_id: Optional[UUID] = None
    course_id: Optional[UUID] = None


class TeamDeletedData(BaseModel):
    team_id: UUID


class TeamPlayerAddedData(BaseModel):
    team_id: UUID
    student_id: UUID


class TeamPlayerRemovedData(BaseModel):
    team_id: UUID
    student_id: UUID


class TeamCreatedV1(EventSchema):
    data: TeamCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "team.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamUpdatedV1(EventSchema):
    data: TeamUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "team.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamDeletedV1(EventSchema):
    data: TeamDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "team.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamPlayerAddedV1(EventSchema):
    data: TeamPlayerAddedData

    @classmethod
    def event_type(cls) -> str:
        return "team.player_added.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamPlayerRemovedV1(EventSchema):
    data: TeamPlayerRemovedData

    @classmethod
    def event_type(cls) -> str:
        return "team.player_removed.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


# ================================================================== #
# Regulation
# ================================================================== #


class RegulationCreatedData(BaseModel):
    regulation_id: UUID
    title: str
    description: str
    file_url: Optional[str] = None


class RegulationUpdatedData(BaseModel):
    regulation_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None


class RegulationDeletedData(BaseModel):
    regulation_id: UUID


class RegulationCreatedV1(EventSchema):
    data: RegulationCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "regulation.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "regulation"


class RegulationUpdatedV1(EventSchema):
    data: RegulationUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "regulation.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "regulation"


class RegulationDeletedV1(EventSchema):
    data: RegulationDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "regulation.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "regulation"
