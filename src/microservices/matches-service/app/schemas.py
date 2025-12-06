"""
Pydantic schemas for Matches Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Match Schemas
class MatchCreate(BaseModel):
    """Schema for creating a match."""

    tournament_id: UUID
    team_home_id: UUID
    team_away_id: UUID
    location: str
    start_time: datetime
    created_by: UUID


class MatchUpdate(BaseModel):
    """Schema for updating a match."""

    location: Optional[str] = None
    start_time: Optional[datetime] = None
    team_home_id: Optional[UUID] = None
    team_away_id: Optional[UUID] = None
    updated_by: UUID


class MatchResult(BaseModel):
    """Schema for registering match result."""

    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    registered_by: UUID
    additional_details: Optional[dict] = None


class PlayerLineup(BaseModel):
    """Schema for a player in lineup."""

    player_id: UUID
    jersey_number: int
    is_starter: Optional[bool] = True


class MatchLineup(BaseModel):
    """Schema for match lineup."""

    team_id: UUID
    players: List[PlayerLineup]


class MatchComment(BaseModel):
    """Schema for match comment."""

    message: str
    author_id: UUID
    created_at: Optional[datetime] = None


class MatchResponse(BaseModel):
    """Schema for match response."""

    id: UUID
    tournament_id: UUID
    team_home_id: UUID
    team_away_id: UUID
    location: str
    start_time: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LineupResponse(BaseModel):
    """Schema for lineup response."""

    id: UUID
    match_id: UUID
    team_id: UUID
    player_id: UUID
    jersey_number: int
    is_starter: bool

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Schema for comment response."""

    id: UUID
    match_id: UUID
    message: str
    author_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
