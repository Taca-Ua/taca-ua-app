"""
Tournament-related schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ModalityInfo(BaseModel):
    """Nested modality information"""

    id: int
    name: str


class SeasonInfo(BaseModel):
    """Nested season information"""

    id: int
    year: int
    display_name: str


class TournamentPublicList(BaseModel):
    """Model for listing public tournaments"""

    id: int
    name: str
    modality: ModalityInfo
    season: SeasonInfo
    status: str  # draft, active, finished
    start_date: Optional[datetime] = None
    team_count: int = 0


class TournamentRankingEntry(BaseModel):
    """Model for a tournament ranking entry"""

    position: int
    team_id: int
    team_name: str
    course_id: int
    course_name: str
    course_short_code: str
    points: int
    played: int
    won: int
    drawn: int
    lost: int


class TournamentRankings(BaseModel):
    """Model for tournament rankings"""

    tournament_id: int
    tournament_name: str
    modality_id: int
    modality_name: str
    season_id: int
    season_year: int
    rankings: List[TournamentRankingEntry]


class TournamentPublicDetail(BaseModel):
    """Model for tournament details"""

    id: int
    name: str
    modality: ModalityInfo
    season: SeasonInfo
    status: str
    rules: Optional[str] = None
    start_date: Optional[datetime] = None
    team_count: int = 0
    rankings: Optional[List[TournamentRankingEntry]] = None
