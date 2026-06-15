from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for Course events
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


# event schemas for Course events
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
