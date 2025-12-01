"""
Tournament-related schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TournamentPublicList(BaseModel):
    """Model for listing public tournaments"""

    id: int
    name: str
    modality_id: int
    modality_name: str
    season_id: int
    season_year: int
    status: str  # draft, active, finished
    start_date: Optional[datetime] = None


class TournamentPublicDetail(BaseModel):
    """Model for tournament details"""

    id: int
    name: str
    modality_id: int
    modality_name: str
    season_id: int
    season_year: int
    status: str
    rules: Optional[str] = None
    start_date: Optional[datetime] = None
    teams: List[int]
    team_names: List[str]
