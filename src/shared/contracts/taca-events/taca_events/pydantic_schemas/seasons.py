"""
Typed Pydantic event schemas for the Season domain.
"""

from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema

# ================================================================== #
# Data payload models
# ================================================================== #


class SeasonCreatedData(BaseModel):
    season_id: UUID
    year: int


class SeasonStartedData(BaseModel):
    season_id: UUID
    year: int


class SeasonFinishedData(BaseModel):
    season_id: UUID
    year: int


# ================================================================== #
# EventSchema subclasses
# ================================================================== #


class SeasonCreatedV1(EventSchema):
    data: SeasonCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "season.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "season"


class SeasonStartedV1(EventSchema):
    data: SeasonStartedData

    @classmethod
    def event_type(cls) -> str:
        return "season.started.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "season"


class SeasonFinishedV1(EventSchema):
    data: SeasonFinishedData

    @classmethod
    def event_type(cls) -> str:
        return "season.finished.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "season"
