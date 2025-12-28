"""
Pydantic schemas for Ranking Service API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


# Request Schemas
class RecalculateRequest(BaseModel):
    """Schema for recalculate ranking request."""

    season_id: Optional[UUID] = None
    force: Optional[bool] = False


# Response Schemas
class ModalityRankingResponse(BaseModel):
    """Schema for modality ranking response."""

    id: UUID
    modality_id: UUID
    season_id: UUID
    course_id: UUID
    points: float
    details: Optional[dict] = None
    last_updated: datetime

    class Config:
        from_attributes = True


class CourseRankingResponse(BaseModel):
    """Schema for course ranking response."""

    id: UUID
    course_id: UUID
    season_id: UUID
    total_points: float
    modality_breakdown: Optional[dict] = None
    last_updated: datetime

    class Config:
        from_attributes = True


class GeneralRankingResponse(BaseModel):
    """Schema for general ranking response."""

    id: UUID
    season_id: UUID
    course_id: UUID
    position: int
    total_points: float
    last_updated: datetime

    class Config:
        from_attributes = True


class RankingListResponse(BaseModel):
    """Schema for ranking list response."""

    rankings: List[dict]
    total: int
