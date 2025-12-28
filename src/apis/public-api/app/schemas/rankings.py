"""
Rankings-related schemas
"""

from typing import List

from pydantic import BaseModel


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
