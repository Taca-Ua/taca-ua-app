"""
Pydantic schemas for Modalities Service API.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


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
    nucleo_id: Optional[str] = None
    nucleo_name: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== MODALITY TYPE SCHEMAS ====================
class ModalityTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    escaloes: Optional[List[dict]] = None


class ModalityTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    escaloes: Optional[List[dict]] = None


class ModalityTypeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    escaloes: Optional[List[dict]] = None
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
    modality_type_id: Optional[str] = None
    modality_type_name: Optional[str] = None
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
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    student_number: str
    is_member: bool
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


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
    modality_id: Optional[str] = None
    modality_name: Optional[str] = None
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    players: Optional[List[StudentResponse]] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
