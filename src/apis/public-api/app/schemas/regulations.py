"""
Regulation-related schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RegulationPublic(BaseModel):
    """Model for public regulation information"""

    id: int
    title: str
    description: Optional[str] = None
    modality_id: Optional[int] = None
    file_url: str
    created_at: datetime
