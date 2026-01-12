"""
Pydantic schemas for Tournaments Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

# ==================== Tournament Schemas ====================


class TournamentCreate(BaseModel):
    """Schema for creating a tournament"""

    name: str
    modality_id: UUID
    teams_ids: Optional[List[UUID]]
    start_date: Optional[datetime]
    created_by: Optional[UUID] = None


class TournamentUpdate(BaseModel):
    """Schema for updating a tournament"""

    name: Optional[str] = None
    start_date: Optional[datetime] = None
    status: Optional[str] = None
    teams_add: Optional[List[UUID]] = None
    teams_remove: Optional[List[UUID]] = None


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
    teams_ids: List[UUID]

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

        team_id: UUID
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
