"""
Pydantic models for Public Data API
All models follow the API_ENDPOINTS.md specification
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# ================== 1. Calendar (RF5.1) ==================


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


# ================== 2. Results (RF5.2) ==================


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


# ================== 3. Rankings (RF5.3–5.5) ==================


class RankingEntry(BaseModel):
    """Model for a ranking entry"""

    position: int
    course_id: int
    course_name: str
    course_short_code: str
    points: int
    played: int
    won: int
    drawn: int
    lost: int


class ModalityRanking(BaseModel):
    """Model for modality-specific ranking"""

    modality_id: int
    modality_name: str
    rankings: List[RankingEntry]


class CourseRanking(BaseModel):
    """Model for course-specific ranking"""

    course_id: int
    course_name: str
    modalities: List[ModalityRanking]
    total_points: int


class GeneralRanking(BaseModel):
    """Model for general ranking"""

    season_id: int
    season_year: int
    rankings: List[RankingEntry]


class HistoricalRanking(BaseModel):
    """Model for historical rankings"""

    season_id: int
    season_year: int
    winner_course_id: int
    winner_course_name: str
    rankings: List[RankingEntry]


# ================== 4. Tournaments ==================


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


# ================== 5. Modalities ==================


class ModalityPublic(BaseModel):
    """Model for public modality information"""

    id: int
    name: str
    type: str  # coletiva, individual, mista
    description: Optional[str] = None


# ================== 6. Courses ==================


class CoursePublic(BaseModel):
    """Model for public course information"""

    id: int
    name: str
    short_code: str
    color: Optional[str] = None


# ================== 7. Regulations (RF5.6) ==================


class RegulationPublic(BaseModel):
    """Model for public regulation information"""

    id: int
    title: str
    description: Optional[str] = None
    modality_id: Optional[int] = None
    modality_name: Optional[str] = None
    file_url: str
    created_at: datetime


# ================== 8. Historical Data ==================


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
