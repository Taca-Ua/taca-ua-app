"""
Base Snapshot DTO.

All snapshot items extend this base to ensure a common contract across services.
"""

from pydantic import BaseModel


class SnapshotBase(BaseModel):
    """
    Base class for all snapshot DTOs.

    Provides shared Pydantic configuration for all snapshot models.
    All snapshot models must have `from_attributes=True` so they can be
    constructed from ORM objects when providers build snapshot responses.
    """

    model_config = {"from_attributes": True}
