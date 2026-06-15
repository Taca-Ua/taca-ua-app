from pydantic import BaseModel

from .base import EventSchema


# data models for Season events
class SeasonCreatedData(BaseModel):
    season_id: int
    name: str


# event schemas for Season events
class SeasonCreatedV1(EventSchema):
    data: SeasonCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "season.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "season"
