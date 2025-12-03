"""
Calendar-related schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TeamInfo(BaseModel):
    """Nested team information"""

    id: int
    name: str
    course_abbreviation: str


class ModalityInfo(BaseModel):
    """Nested modality information"""

    id: int
    name: str


class MatchPublicList(BaseModel):
    """Model for listing public matches"""

    id: int
    tournament_id: int
    tournament_name: str
    team_home: TeamInfo
    team_away: TeamInfo
    modality: ModalityInfo
    start_time: datetime
    location: str
    status: str  # scheduled, in_progress, finished, cancelled
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class MatchPublicDetail(BaseModel):
    """Model for match details"""

    id: int
    tournament_id: int
    tournament_name: str
    modality: ModalityInfo
    team_home: TeamInfo
    team_away: TeamInfo
    location: str
    start_time: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
