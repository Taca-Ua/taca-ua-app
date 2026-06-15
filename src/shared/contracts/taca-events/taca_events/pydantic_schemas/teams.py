from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema


# data models for Team events
class TeamCreatedData(BaseModel):
    team_id: UUID
    name: str
    modality_id: UUID
    course_id: UUID
    season_id: int


class TeamUpdatedData(BaseModel):
    team_id: UUID
    name: Optional[str] = None
    modality_id: Optional[UUID] = None
    course_id: Optional[UUID] = None


class TeamDeletedData(BaseModel):
    team_id: UUID


class TeamPlayerAddedData(BaseModel):
    team_id: UUID
    student_id: UUID


class TeamPlayerRemovedData(BaseModel):
    team_id: UUID
    student_id: UUID


# event schemas for Team events
class TeamCreatedV1(EventSchema):
    data: TeamCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "team.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamUpdatedV1(EventSchema):
    data: TeamUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "team.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamDeletedV1(EventSchema):
    data: TeamDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "team.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamPlayerAddedV1(EventSchema):
    data: TeamPlayerAddedData

    @classmethod
    def event_type(cls) -> str:
        return "team.player_added.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"


class TeamPlayerRemovedV1(EventSchema):
    data: TeamPlayerRemovedData

    @classmethod
    def event_type(cls) -> str:
        return "team.player_removed.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "team"
