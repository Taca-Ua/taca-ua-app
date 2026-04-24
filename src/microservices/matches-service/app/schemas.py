"""
Pydantic schemas for Matches Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Helper Schemas
class MatchParticipantUpdate(BaseModel):
    """Schema for updating a match participant."""

    participant_id: UUID
    score: Optional[int] = Field(None, ge=0)
    position: Optional[int] = Field(None, ge=1)


class MatchParticipantResponse(BaseModel):
    """Schema for match participant response."""

    participant: UUID
    match_id: UUID
    score: Optional[int] = None
    position: Optional[int] = None

    class Config:
        from_attributes = True


# Match Schemas
class MatchCreate(BaseModel):
    """Schema for creating a match."""

    tournament_id: Optional[UUID] = None
    location: str
    start_time: datetime
    created_by: UUID
    participants: List[UUID] = Field(default_factory=list)


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
    participants: List[MatchParticipantResponse] = Field(default_factory=list)
    comments: Optional[List["CommentResponse"]] = None
    lineups: Optional[List["LineupResponse"]] = None

    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Lineup Schemas
class LineupResponse(BaseModel):
    """Schema for lineup response."""

    participant_id: UUID
    lineup: List[dict] = Field(default_factory=list)


class LineupBatchCreate(BaseModel):
    """Schema for creating multiple lineup entries at once."""

    participant: UUID
    players: List[UUID] = Field(
        ..., description="List of players to assign to the lineup"
    )


# Comment Schemas
class CommentCreate(BaseModel):
    """Schema for creating a comment."""

    message: str = Field(..., min_length=1)
    created_by: UUID


class CommentResponse(BaseModel):
    """Schema for comment response."""

    id: UUID
    # match_id: UUID
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
