"""
Pydantic schemas for Matches Service API requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# MatchParticipant Schemas
class MatchParticipantCreate(BaseModel):
    """Schema for creating a match participant."""

    participant_type: str  # "team" or "athlete"
    team_id: Optional[UUID] = None
    athlete_id: Optional[UUID] = None


class MatchParticipantUpdate(BaseModel):
    """Schema for updating a match participant."""

    participant_id: UUID
    score: Optional[int] = Field(None, ge=0)
    position: Optional[int] = Field(None, ge=1)
    result_metadata: Optional[Dict[str, Any]] = None


class MatchParticipantResponse(BaseModel):
    """Schema for match participant response."""

    id: UUID
    match_id: UUID
    participant_type: str
    team_id: Optional[UUID] = None
    athlete_id: Optional[UUID] = None
    score: Optional[int] = None
    position: Optional[int] = None
    result_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Match Schemas
class MatchCreate(BaseModel):
    """Schema for creating a match."""

    tournament_id: Optional[UUID] = None
    location: str
    start_time: datetime
    created_by: UUID
    participants: List[MatchParticipantCreate] = Field(default_factory=list)


class MatchUpdate(BaseModel):
    """Schema for updating a match."""

    location: Optional[str] = None
    start_time: Optional[datetime] = None
    status: Optional[str] = None  # "scheduled", "in_progress", "finished", "cancelled"


class MatchResponse(BaseModel):
    """Schema for match response."""

    id: UUID
    tournament_id: Optional[UUID] = None
    location: str
    start_time: datetime
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    participants: List[MatchParticipantResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Lineup Schemas
class LineupCreate(BaseModel):
    """Schema for creating a lineup entry."""

    team_id: UUID
    player_id: UUID
    jersey_number: int = Field(..., ge=0)
    is_starter: bool = True


class LineupBatchCreate(BaseModel):
    """Schema for creating multiple lineup entries at once."""

    team_id: UUID
    players: List[dict] = Field(
        ...,
        description="List of players with player_id, jersey_number, and is_starter",
    )


class LineupResponse(BaseModel):
    """Schema for lineup response."""

    id: UUID
    match_id: UUID
    team_id: UUID
    player_id: UUID
    jersey_number: int
    is_starter: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Comment Schemas
class CommentCreate(BaseModel):
    """Schema for creating a comment."""

    message: str = Field(..., min_length=1)
    created_by: UUID


class CommentResponse(BaseModel):
    """Schema for comment response."""

    id: UUID
    match_id: UUID
    message: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Result Schemas
class MatchResultUpdate(BaseModel):
    """Schema for updating match results."""

    participant_results: List[MatchParticipantUpdate] = Field(
        ..., description="List of participant results with scores/positions"
    )
    status: Optional[str] = Field(
        "finished", description="Match status after result update"
    )
