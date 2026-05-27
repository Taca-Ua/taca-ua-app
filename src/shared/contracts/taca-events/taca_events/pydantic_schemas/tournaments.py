"""
Typed Pydantic event schemas for the Tournaments Service.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema

# ================================================================== #
# Data payload models
# ================================================================== #


class TournamentCreatedData(BaseModel):
    tournament_id: UUID
    modality_id: UUID
    name: str
    start_date: str  # ISO 8601 date string
    status: str
    scoring_format_id: UUID
    season_id: int
    format_type: str


class TournamentUpdatedData(BaseModel):
    tournament_id: UUID
    name: Optional[str] = None
    start_date: Optional[str] = None
    status: Optional[str] = None
    scoring_format_id: Optional[UUID] = None


class TournamentDeletedData(BaseModel):
    tournament_id: UUID


class RankingEntryData(BaseModel):
    """Single ranking entry in a finished tournament."""

    competitor_id: UUID
    position: int


class TournamentFinishedData(BaseModel):
    tournament_id: UUID
    ranking_entries: List[RankingEntryData] = []


class TournamentCompetitorAddedData(BaseModel):
    tournament_id: UUID
    competitor_type: str  # "team" | "athlete"
    competitor_entity_id: UUID
    competitor_id: UUID
    competitor_course_id: UUID


class TournamentCompetitorDeletedData(BaseModel):
    competitor_id: Optional[UUID] = None
    tournament_id: UUID
    competitor_entity_id: Optional[UUID] = None


class TournamentStandingsUpdatedData(BaseModel):
    tournament_id: UUID
    format_type: str
    standings: list


# ================================================================== #
# EventSchema subclasses
# ================================================================== #


class TournamentCreatedV1(EventSchema):
    data: TournamentCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "tournament.created.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "tournament"


class TournamentUpdatedV1(EventSchema):
    data: TournamentUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "tournament.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "tournament"


class TournamentDeletedV1(EventSchema):
    data: TournamentDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "tournament.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "tournament"


class TournamentFinishedV1(EventSchema):
    data: TournamentFinishedData

    @classmethod
    def event_type(cls) -> str:
        return "tournament.finished.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "tournament"


class TournamentCompetitorAddedV1(EventSchema):
    data: TournamentCompetitorAddedData

    @classmethod
    def event_type(cls) -> str:
        return "tournament.competitor.added.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "tournament"


class TournamentCompetitorDeletedV1(EventSchema):
    data: TournamentCompetitorDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "tournament.competitor.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "tournament"


class TournamentStandingsUpdatedV1(EventSchema):
    data: TournamentStandingsUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "tournament.standings.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "tournament"
