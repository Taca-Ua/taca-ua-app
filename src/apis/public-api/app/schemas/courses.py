"""
Course-related schemas
"""

from typing import Optional

from pydantic import BaseModel


class CoursePublic(BaseModel):
    """Model for public course information"""

    id: int
    name: str
    short_code: str
    color: Optional[str] = None
