"""
Service for communicating with tournaments-service microservice
"""

import os
from typing import Any, Dict, List, Optional
from uuid import UUID

from .base_service import BaseService


class TournamentsService(BaseService):
    """Service for managing tournaments via tournaments-service"""

    def __init__(self):
        base_url = os.environ.get(
            "TOURNAMENTS_SERVICE_URL", "http://tournaments-service:8000"
        )
        super().__init__(base_url)

    def list_tournaments(
        self, status_filter: Optional[str] = None, modality_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        List all tournaments with optional filters

        Args:
            status_filter: Filter by status (draft, active, finished)
            modality_id: Filter by modality ID

        Returns:
            List of tournament dictionaries
        """
        params = {}
        if status_filter:
            params["status_filter"] = status_filter
        if modality_id:
            params["modality_id"] = str(modality_id)

        return self.get("/tournaments", params=params)

    def get_tournament(self, tournament_id: UUID) -> Dict[str, Any]:
        """
        Get a tournament by ID

        Args:
            tournament_id: Tournament ID

        Returns:
            Tournament dictionary
        """
        return self.get(f"/tournaments/{tournament_id}")

    def create_tournament(
        self,
        modality_id: UUID,
        name: str,
        created_by: UUID,
        start_date: Optional[str] = None,
        teams_ids: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new tournament

        Args:
            modality_id: ID of the modality
            name: Tournament name
            created_by: ID of the user creating the tournament
            start_date: Optional start date (ISO format)
            teams_ids: Optional list of team IDs

        Returns:
            Created tournament dictionary
        """
        data = {
            "modality_id": str(modality_id),
            "name": name,
            "created_by": str(created_by),
        }
        if start_date:
            data["start_date"] = start_date
        if teams_ids:
            data["teams_ids"] = [str(team_id) for team_id in teams_ids]
        else:
            data["teams_ids"] = []

        return self.post("/tournaments", data=data)

    def update_tournament(
        self,
        tournament_id: UUID,
        name: Optional[str] = None,
        start_date: Optional[str] = None,
        status: Optional[str] = None,
        competitors_add: Optional[List[UUID]] = None,
        competitors_remove: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        """
        Update a tournament

        Args:
            tournament_id: Tournament ID
            name: New tournament name
            start_date: New start date (ISO format)
            status: New status (draft, active, finished)
            competitors_add: Team IDs to add
            competitors_remove: Team IDs to remove

        Returns:
            Updated tournament dictionary
        """
        data = {}
        if name is not None:
            data["name"] = name
        if start_date is not None:
            data["start_date"] = start_date
        if status is not None:
            data["status"] = status
        if competitors_add is not None:
            data["competitors_add"] = [competitor for competitor in competitors_add]
        if competitors_remove is not None:
            data["competitors_remove"] = [
                competitor for competitor in competitors_remove
            ]

        print("Update tournament data:", data)
        return self.put(f"/tournaments/{tournament_id}", data=data)

    def delete_tournament(self, tournament_id: UUID) -> None:
        """
        Delete a tournament

        Args:
            tournament_id: Tournament ID
        """
        self.delete(f"/tournaments/{tournament_id}")

    def finish_tournament(
        self,
        tournament_id: UUID,
        ranking_entries: List[Dict[str, Any]],
        finished_by: UUID,
    ) -> Dict[str, Any]:
        """
        Mark a tournament as finished and set final rankings

        Args:
            tournament_id: Tournament ID
            ranking_entries: List of dicts with team_id and position
            finished_by: ID of the user finishing the tournament

        Returns:
            Updated tournament dictionary
        """
        data = {
            "ranking_entries": ranking_entries,
            "finished_by": str(finished_by),
        }
        return self.post(f"/tournaments/{tournament_id}/finish", data=data)


# Singleton instance
tournaments_service_client = TournamentsService()
