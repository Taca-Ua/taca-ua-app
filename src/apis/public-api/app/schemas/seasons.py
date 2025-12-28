"""
Season-related schemas
"""

from pydantic import BaseModel


class SeasonPublic(BaseModel):
    """Model for public season information"""

    id: int
    year: int
    status: str  # draft, active, finished
