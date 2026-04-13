"""
Service for communicating with tournaments-service for season management.
"""

import os
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from .base_service import BaseService


@dataclass
class SeasonDTO:
    id: str  # UUID as string
    year: int
    status: str  # "draft", "active", "finished"
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class SeasonService(BaseService):
    """Service for managing seasons via tournaments-service"""

    def __init__(self):
        base_url = os.environ.get(
            "TOURNAMENTS_SERVICE_URL", "http://tournaments-service:8000"
        )
        super().__init__(base_url)

    def list_seasons(self) -> List[SeasonDTO]:
        """List all seasons."""
        data = self.get("/seasons")
        return [SeasonDTO(**s) for s in data]

    def create_season(self, year: int) -> SeasonDTO:
        """Create a new draft season."""
        data = self.post("/seasons", data={"year": year})
        return SeasonDTO(**data)

    def start_season(self, season_id: UUID) -> SeasonDTO:
        """Start (activate) a draft season."""
        data = self.post(f"/seasons/{season_id}/start", data={})
        return SeasonDTO(**data)

    def finish_season(self, season_id: UUID) -> SeasonDTO:
        """Finish an active season."""
        data = self.post(f"/seasons/{season_id}/finish", data={})
        return SeasonDTO(**data)


seasons_service_client = SeasonService()
