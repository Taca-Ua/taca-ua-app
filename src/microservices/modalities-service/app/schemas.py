"""
Pydantic schemas for Modalities Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


# Course Schemas
class CourseCreate(BaseModel):
    """Schema for creating a course."""

    name: str
    abbreviation: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_by: UUID


class CourseUpdate(BaseModel):
    """Schema for updating a course."""

    name: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    updated_by: UUID


class CourseResponse(BaseModel):
    """Schema for course response."""

    id: UUID
    name: str
    abbreviation: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Modality Schemas
class ModalityCreate(BaseModel):
    """Schema for creating a modality."""

    name: str
    type: str  # "coletiva", "individual", "mista"
    scoring_schema: Optional[dict] = None
    created_by: UUID


class ModalityUpdate(BaseModel):
    """Schema for updating a modality."""

    name: Optional[str] = None
    type: Optional[str] = None
    scoring_schema: Optional[dict] = None
    updated_by: UUID


class ModalityResponse(BaseModel):
    """Schema for modality response."""

    id: UUID
    name: str
    type: str
    scoring_schema: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Team Schemas
class TeamCreate(BaseModel):
    """Schema for creating a team."""

    modality_id: UUID
    course_id: UUID
    name: Optional[str] = None
    players: Optional[List[UUID]] = None
    created_by: UUID


class TeamUpdate(BaseModel):
    """Schema for updating a team."""

    name: Optional[str] = None
    players_add: Optional[List[UUID]] = None
    players_remove: Optional[List[UUID]] = None
    updated_by: UUID


class TeamResponse(BaseModel):
    """Schema for team response."""

    id: UUID
    modality_id: UUID
    course_id: UUID
    name: str
    players: Optional[List[UUID]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Student Schemas
class StudentCreate(BaseModel):
    """Schema for creating a student."""

    course_id: UUID
    full_name: str
    student_number: str
    email: Optional[str] = None
    is_member: Optional[bool] = False
    created_by: UUID


class StudentUpdate(BaseModel):
    """Schema for updating a student."""

    full_name: Optional[str] = None
    email: Optional[str] = None
    is_member: Optional[bool] = None
    updated_by: UUID


class StudentResponse(BaseModel):
    """Schema for student response."""

    id: UUID
    course_id: UUID
    full_name: str
    student_number: str
    email: Optional[str] = None
    is_member: bool
    created_at: datetime

    class Config:
        from_attributes = True
