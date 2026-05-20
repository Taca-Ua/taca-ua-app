"""
Pydantic schemas for Tournaments Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

# ==================== Tournament Schemas ====================


class CompetitorInput(BaseModel):
    """Schema for competitor input (team or athlete)"""

    competitor_type: str  # "team" or "athlete"
    competitor_entity_id: UUID  # team_id or athlete_id depending on competitor_type
    competitor_course_id: UUID = None

    @field_validator("competitor_type")
    @classmethod
    def validate_competitor_type(cls, v):
        if v not in ["team", "athlete"]:
            raise ValueError('competitor_type must be "team" or "athlete"')
        return v


class CompetitorResponse(BaseModel):
    """Schema for competitor response"""

    id: UUID
    tournament_id: UUID
    competitor_type: str
    competitor: dict  # Contains either {"team_id": UUID} or {"athlete_id": UUID}
    competitor_entity_id: UUID  # team_id or athlete_id depending on competitor_type
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
    season_id: int
    format: Optional[str] = "free"
    format_data: Optional[dict] = None  # Additional data for specific formats


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

    # id: UUID
    # tournament_id: UUID
    competitor_id: UUID
    position: int
    # created_at: datetime

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
    competitors: List[CompetitorResponse]
    competitor_type: str
    season_id: int
    format: str
    format_data: Optional[dict] = None

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


class TournamentSeasonSummaryRequest(BaseModel):
    """Schema for tournament season summary request"""

    season_id: int
    teams_ids: Optional[List[UUID]] = None
    athletes_ids: Optional[List[UUID]] = None


class TournamentSeasonSummary(BaseModel):
    """Schema for tournament season summary"""

    class _TournamentSeasonSummaryCompetitors(BaseModel):
        tournament_id: UUID
        competitors_ids: List[UUID]

    tournaments_finished: int
    tournaments_ongoing: int
    tournaments_scheduled: int

    tournaments_ids: List[UUID]

    competitors_distribution: Optional[List[_TournamentSeasonSummaryCompetitors]] = None


class TournamentStandingsResponse(BaseModel):
    """Schema for tournament standings response"""

    class _TournamentStandingsEntry(BaseModel):
        competitor_id: UUID
        position: int
        format_meta: Optional[dict] = (
            None  # Format-specific metadata (e.g., points, wins, losses)
        )

    standings: Optional[List[_TournamentStandingsEntry]] = None

    class Config:
        from_attributes = True


class TournamentFormatMetaUpdate(BaseModel):
    """Schema for updating tournament format meta"""

    format_meta: dict  # Format-specific metadata to update


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
