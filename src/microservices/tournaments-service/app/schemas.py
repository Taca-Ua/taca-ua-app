"""
Pydantic schemas for Tournaments Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


# ==================== Season Schemas ====================


class SeasonCreate(BaseModel):
    """Schema for creating a season"""

    year: int


class SeasonResponse(BaseModel):
    """Schema for season response"""

    id: UUID
    year: int
    status: str
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== Tournament Schemas ====================


class CompetitorInput(BaseModel):
    """Schema for competitor input (team or athlete)"""

    competitor_type: str  # "team" or "athlete"
    team_id: Optional[UUID] = None
    athlete_id: Optional[UUID] = None
    competitor_course_id: Optional[UUID] = None

    @field_validator("competitor_type")
    @classmethod
    def validate_competitor_type(cls, v):
        if v not in ["team", "athlete"]:
            raise ValueError('competitor_type must be "team" or "athlete"')
        return v

    @field_validator("team_id")
    @classmethod
    def validate_team_id(cls, v, info):
        if info.data.get("competitor_type") == "team" and v is None:
            raise ValueError('team_id is required when competitor_type is "team"')
        return v

    @field_validator("athlete_id")
    @classmethod
    def validate_athlete_id(cls, v, info):
        if info.data.get("competitor_type") == "athlete" and v is None:
            raise ValueError('athlete_id is required when competitor_type is "athlete"')
        return v


class CompetitorResponse(BaseModel):
    """Schema for competitor response"""

    id: UUID
    tournament_id: UUID
    competitor_type: str
    competitor: dict  # Contains either {"team_id": UUID} or {"athlete_id": UUID}
    created_at: datetime

    class Config:
        from_attributes = True


class TournamentCreate(BaseModel):
    """Schema for creating a tournament"""

    name: str
    modality_id: UUID
    scoring_format_id: UUID
    start_date: Optional[datetime]
    competitor_type: str  # "team" or "athlete"
    season_id: Optional[UUID] = None


class TournamentUpdate(BaseModel):
    """Schema for updating a tournament"""

    name: Optional[str] = None
    start_date: Optional[datetime] = None
    status: Optional[str] = None
    competitors_add: List[CompetitorInput] = None
    competitors_remove: List[UUID] = None  # competitor IDs to remove
    scoring_format_id: Optional[UUID] = None


class TournamentRankingPositionSchema(BaseModel):
    """Schema for tournament ranking position"""

    id: UUID
    tournament_id: UUID
    team_id: UUID
    position: int
    created_at: datetime

    class Config:
        from_attributes = True


class TournamentResponse(BaseModel):
    """Schema for tournament response"""

    id: UUID
    name: str
    status: str
    modality_id: UUID
    start_date: Optional[datetime]
    scoring_format_id: UUID
    season_id: Optional[UUID] = None
    competitors: List[CompetitorResponse]
    competitor_type: str

    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    finished_at: Optional[datetime]
    finished_by: Optional[UUID]
    ranking_positions: Optional[List[TournamentRankingPositionSchema]] = None

    class Config:
        from_attributes = True


class TournamentFinish(BaseModel):
    """Schema for finishing a tournament"""

    class TournamentFinishEntry(BaseModel):
        """Schema for tournament finish entry"""

        competitor_id: UUID
        position: int

    ranking_entries: List[TournamentFinishEntry]
    finished_by: UUID


# ==================== Outbox Schemas ====================


class OutboxEventResponse(BaseModel):
    """Schema for outbox event response"""

    id: UUID
    event_type: str
    aggregate_type: str
    aggregate_id: UUID
    payload: dict
    published: bool
    published_at: Optional[datetime]
    created_at: datetime
    retry_count: int
    last_error: Optional[str]

    class Config:
        from_attributes = True
