"""
Team-related schemas
"""

from typing import Optional

from pydantic import BaseModel


class TeamPublic(BaseModel):
    """Model for public team information"""

    id: int
    name: str
    course_id: int
    course_name: str
    course_short_code: str
    modality_id: int
    modality_name: str
    player_count: Optional[int] = None
