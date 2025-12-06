"""
Pydantic schemas for Tournaments Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Request Schemas
class TournamentCreate(BaseModel):
    """Schema for creating a tournament."""

    modality_id: UUID
    name: str
    season_id: UUID
    rules: Optional[dict] = None
    teams: Optional[List[UUID]] = None
    start_date: Optional[datetime] = None
    created_by: UUID


class TournamentUpdate(BaseModel):
    """Schema for updating a tournament."""

    name: Optional[str] = None
    rules: Optional[dict] = None
    teams: Optional[List[UUID]] = None
    start_date: Optional[datetime] = None
    updated_by: UUID


class TournamentTeamsAdd(BaseModel):
    """Schema for adding teams to a tournament."""

    team_ids: List[UUID] = Field(..., min_length=1)


class TournamentTeamsRemove(BaseModel):
    """Schema for removing teams from a tournament."""

    team_ids: List[UUID] = Field(..., min_length=1)


class TournamentFinish(BaseModel):
    """Schema for finishing a tournament."""

    finished_by: UUID


# Response Schemas
class TournamentResponse(BaseModel):
    """Schema for tournament response."""

    id: UUID
    modality_id: UUID
    name: str
    season_id: UUID
    status: str
    rules: Optional[dict] = None
    start_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TournamentListResponse(BaseModel):
    """Schema for tournament list response."""

    tournaments: List[TournamentResponse]
    total: int
    limit: int
    offset: int
