"""
Typed Pydantic event schemas for the Modalities Service.

Covers: Nucleo, Course, ModalityType, Modality, Student, Staff, Team,
TeamPlayer events.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for Modality events
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


# event schemas for Modality events
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
