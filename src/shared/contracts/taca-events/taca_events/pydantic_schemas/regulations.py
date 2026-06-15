from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for Regulation events
class RegulationCreatedData(BaseModel):
    regulation_id: UUID
    title: str
    description: str
    file_url: Optional[str] = None
    season_id: int


class RegulationUpdatedData(BaseModel):
    regulation_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None


class RegulationDeletedData(BaseModel):
    regulation_id: UUID


# event schemas for Regulation events
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
