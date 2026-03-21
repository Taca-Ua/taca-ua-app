"""
Pydantic schemas for Modalities Service API.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== NUCLEO SCHEMAS ====================
class NucleoCreate(BaseModel):
    name: str
    abbreviation: str


class NucleoUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None


class NucleoResponse(BaseModel):
    id: str
    name: str
    abbreviation: str
    admins_ids: List[str] = Field(default_factory=list)
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== COURSE SCHEMAS ====================
class CourseCreate(BaseModel):
    name: str
    abbreviation: str
    nucleo_id: UUID


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    abbreviation: Optional[str] = None
    nucleo_id: Optional[UUID] = None


class CourseResponse(BaseModel):
    id: str
    name: str
    abbreviation: str
    nucleo: NucleoResponse
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== MODALITY TYPE SCHEMAS ====================
class _Escalao(BaseModel):
    escalao: str
    minParticipants: Optional[int] = None
    maxParticipants: Optional[int] = None
    points: List[int]

    def to_dict(self):
        return {
            "escalao": self.escalao,
            "minParticipants": self.minParticipants,
            "maxParticipants": self.maxParticipants,
            "points": self.points,
        }


class ModalityTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    escaloes: Optional[List[_Escalao]] = None
    is_playoff: bool = False
    tournament_competitor_type: Optional[str] = None

    def escaloes_encoder(self):
        if not self.escaloes:
            return []

        escaloes_list = []
        for escalao in self.escaloes:
            escaloes_list.append(escalao.to_dict())

        return escaloes_list


class ModalityTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    escaloes: Optional[List[_Escalao]] = None
    is_playoff: Optional[bool] = None
    tournament_competitor_type: Optional[str] = None

    def escaloes_encoder(self):
        if not self.escaloes:
            return []

        escaloes_list = []
        for escalao in self.escaloes:
            escaloes_list.append(escalao.to_dict())

        return escaloes_list


class ModalityTypeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    escaloes: Optional[List[_Escalao]] = None
    is_playoff: bool = False
    tournament_competitor_type: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== MODALITY SCHEMAS ====================
class ModalityCreate(BaseModel):
    name: str
    modality_type_id: UUID


class ModalityUpdate(BaseModel):
    name: Optional[str] = None
    modality_type_id: Optional[UUID] = None


class ModalityResponse(BaseModel):
    id: str
    name: str
    modality_type: ModalityTypeResponse
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== STUDENT SCHEMAS ====================
class StudentCreate(BaseModel):
    full_name: str
    course_id: UUID
    student_number: str
    is_member: bool = False


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    course_id: Optional[UUID] = None
    student_number: Optional[str] = None
    is_member: Optional[bool] = None


class StudentResponse(BaseModel):
    id: str
    full_name: str
    course: CourseResponse
    student_number: str
    is_member: bool
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class StudentMembershipSyncRequest(BaseModel):
    """NMEC values to mark as sócios after resetting everyone in scope to não-sócio."""

    student_numbers: List[str] = Field(default_factory=list)


class StudentMembershipSyncResponse(BaseModel):
    participants_in_scope: int
    reset_to_non_socio: int
    set_as_socio: int
    # NMECs no ficheiro que não correspondem a nenhum participante no âmbito
    unmatched_numbers: List[str]


# ==================== STAFF SCHEMAS ====================
class StaffCreate(BaseModel):
    full_name: str
    staff_number: Optional[str] = None
    contact: Optional[str] = None


class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    staff_number: Optional[str] = None
    contact: Optional[str] = None


class StaffResponse(BaseModel):
    id: str
    full_name: str
    staff_number: Optional[str] = None
    contact: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== TEAM SCHEMAS ====================
class TeamCreate(BaseModel):
    name: str
    modality_id: UUID
    course_id: UUID


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    modality_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    players_add: Optional[List[UUID]] = None
    players_remove: Optional[List[UUID]] = None


class TeamResponse(BaseModel):
    id: str
    name: str
    modality: ModalityResponse
    course: CourseResponse
    players: List[StudentResponse] = Field(default_factory=list)
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== REGULATION SCHEMAS ====================


class RegulationInternalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: str


class RegulationResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    file_url: str

    class Config:
        from_attributes = True
