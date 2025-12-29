"""
Pydantic schemas for Tournaments Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

# ==================== Tournament Schemas ====================


class TournamentBase(BaseModel):
    """Base schema for Tournament"""

    name: str = Field(..., description="Tournament name")
    modality_id: UUID = Field(..., description="ID of the modality")
    start_date: Optional[datetime] = Field(None, description="Tournament start date")


class TournamentCreate(TournamentBase):
    """Schema for creating a tournament"""

    team_ids: Optional[List[UUID]] = Field(
        default_factory=list, description="List of team IDs to include"
    )
    created_by: UUID = Field(..., description="ID of the user creating the tournament")


class TournamentUpdate(BaseModel):
    """Schema for updating a tournament"""

    name: Optional[str] = Field(None, description="Tournament name")
    start_date: Optional[datetime] = Field(None, description="Tournament start date")
    status: Optional[str] = Field(
        None, description="Tournament status (draft, active, finished)"
    )
    teams_add: Optional[List[UUID]] = Field(
        default_factory=list, description="Team IDs to add"
    )
    teams_remove: Optional[List[UUID]] = Field(
        default_factory=list, description="Team IDs to remove"
    )


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
    modality_id: UUID
    name: str
    status: str
    start_date: Optional[datetime]
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    finished_at: Optional[datetime]
    finished_by: Optional[UUID]
    ranking_positions: Optional[List[TournamentRankingPositionSchema]] = None

    class Config:
        from_attributes = True


class TournamentFinishEntry(BaseModel):
    """Schema for tournament finish entry"""

    team_id: UUID = Field(..., description="ID of the team")
    position: int = Field(..., description="Position in the tournament")


class TournamentFinish(BaseModel):
    """Schema for finishing a tournament"""

    ranking_entries: List[TournamentFinishEntry] = Field(
        ..., description="List of team rankings"
    )
    finished_by: UUID = Field(
        ..., description="ID of the user finishing the tournament"
    )


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
