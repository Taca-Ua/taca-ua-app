"""
Modality-related schemas
"""

from typing import Optional

from pydantic import BaseModel


class ModalityPublic(BaseModel):
    """Model for public modality information"""

    id: int
    name: str
    type: str  # coletiva, individual, mista
    scoring_schema: Optional[dict] = None
