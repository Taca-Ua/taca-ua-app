from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for Student events
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


# event schemas for Student events
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
