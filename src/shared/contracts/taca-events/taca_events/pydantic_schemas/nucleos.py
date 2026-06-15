from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for Nucleo events
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


# event schemas for Nucleo events
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
