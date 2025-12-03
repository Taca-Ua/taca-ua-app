"""
Season-related schemas
"""

from pydantic import BaseModel


class SeasonPublic(BaseModel):
    """Model for public season information"""

    id: int
    year: int
    display_name: str  # e.g., "25/26"
    is_active: bool
