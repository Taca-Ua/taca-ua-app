from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for ModalityType events
class _EscalaoData(BaseModel):
    name: str
    min_participants: Optional[int] = None
    max_participants: Optional[int] = None
    points: list[int]


class ModalityTypeCreatedData(BaseModel):

    modality_type_id: UUID
    season_id: int
    name: str
    description: Optional[str] = None
    mode: str
    escaloes: list[_EscalaoData]


class ModalityTypeUpdatedData(BaseModel):
    modality_type_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    escaloes: Optional[list[_EscalaoData]] = None


class ModalityTypeDeletedData(BaseModel):
    modality_type_id: UUID


# event schemas for ModalityType events
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
