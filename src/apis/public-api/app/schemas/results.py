"""
Results-related schemas
"""

from datetime import datetime

from pydantic import BaseModel


class ResultPublic(BaseModel):
    """Model for public results"""

    match_id: int
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
    home_score: int
    away_score: int
    match_date: datetime
