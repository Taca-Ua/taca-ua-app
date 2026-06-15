from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for Staff events
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


# event schemas for Staff events
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
