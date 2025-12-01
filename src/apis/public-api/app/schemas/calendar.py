"""
Calendar-related schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MatchPublicList(BaseModel):
    """Model for listing public matches"""

    id: int
    tournament_id: int
    modality_id: int
    team_home_id: int
    team_away_id: int
    team_home_name: str
    team_away_name: str
    course_home_id: int
    course_away_id: int
    location: str
    start_time: datetime
    status: str  # scheduled, finished
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class MatchPublicDetail(BaseModel):
    """Model for match details"""

    id: int
    tournament_id: int
    tournament_name: str
    modality_id: int
    modality_name: str
    team_home_id: int
    team_away_id: int
    team_home_name: str
    team_away_name: str
    course_home_id: int
    course_away_id: int
    course_home_name: str
    course_away_name: str
    location: str
    start_time: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    comments: Optional[List[str]] = []
