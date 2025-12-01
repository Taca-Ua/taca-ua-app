"""
Historical data schemas
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel

from .rankings import RankingEntry


class HistoricalMatch(BaseModel):
    """Model for historical match data"""

    id: int
    season_id: int
    season_year: int
    tournament_name: str
    modality_name: str
    team_home_name: str
    team_away_name: str
    course_home_name: str
    course_away_name: str
    location: str
    start_time: datetime
    home_score: int
    away_score: int


class HistoricalRanking(BaseModel):
    """Model for historical rankings"""

    season_id: int
    season_year: int
    winner_course_id: int
    winner_course_name: str
    rankings: List[RankingEntry]
