"""
Service for communicating with tournaments-service microservice
"""

import os
from typing import Any, Dict, List, Optional

from .base_service import BaseService


class TournamentsService(BaseService):
    """Service for managing tournaments via tournaments-service"""

    def __init__(self):
        base_url = os.environ.get(
            "TOURNAMENTS_SERVICE_URL", "http://tournaments-service:8000"
        )
        super().__init__(base_url)

    def create_tournament(
        self,
        modality_id: str,
        name: str,
        season_id: str,
        created_by: str,
        rules: Optional[Dict[str, Any]] = None,
        teams: Optional[List[str]] = None,
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new tournament

        Args:
            modality_id: UUID of the modality
            name: Tournament name
            season_id: UUID of the season
            created_by: UUID of the user creating the tournament
            rules: Optional tournament rules (JSON)
            teams: Optional list of team UUIDs
            start_date: Optional start date (ISO 8601)

        Returns:
            Created tournament data
        """
        data = {
            "modality_id": modality_id,
            "name": name,
            "season_id": season_id,
            "created_by": created_by,
        }

        if rules is not None:
            data["rules"] = rules
        if teams is not None:
            data["teams"] = teams
        if start_date is not None:
            data["start_date"] = start_date

        return self.post("/tournaments", data)

    def list_tournaments(
        self,
        modality_id: Optional[str] = None,
        season_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List tournaments with optional filters

        Args:
            modality_id: Filter by modality
            season_id: Filter by season
            status: Filter by status (draft, active, finished)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of tournaments
        """
        params = {"limit": limit, "offset": offset}

        if modality_id:
            params["modality_id"] = modality_id
        if season_id:
            params["season_id"] = season_id
        if status:
            params["status"] = status

        return self.get("/tournaments", params=params)

    def get_tournament(self, tournament_id: str) -> Dict[str, Any]:
        """
        Get tournament details

        Args:
            tournament_id: UUID of the tournament

        Returns:
            Tournament data
        """
        return self.get(f"/tournaments/{tournament_id}")

    def update_tournament(
        self,
        tournament_id: str,
        updated_by: str,
        name: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None,
        teams: Optional[List[str]] = None,
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a tournament

        Args:
            tournament_id: UUID of the tournament
            updated_by: UUID of the user updating
            name: Optional new name
            rules: Optional new rules
            teams: Optional new team list (replaces existing)
            start_date: Optional new start date

        Returns:
            Updated tournament data
        """
        data = {"updated_by": updated_by}

        if name is not None:
            data["name"] = name
        if rules is not None:
            data["rules"] = rules
        if teams is not None:
            data["teams"] = teams
        if start_date is not None:
            data["start_date"] = start_date

        return self.put(f"/tournaments/{tournament_id}", data)

    def add_teams(self, tournament_id: str, team_ids: List[str]) -> Dict[str, Any]:
        """
        Add teams to tournament

        Args:
            tournament_id: UUID of the tournament
            team_ids: List of team UUIDs to add

        Returns:
            Response data
        """
        data = {"team_ids": team_ids}
        return self.post(f"/tournaments/{tournament_id}/teams", data)

    def remove_teams(self, tournament_id: str, team_ids: List[str]) -> Dict[str, Any]:
        """
        Remove teams from tournament

        Args:
            tournament_id: UUID of the tournament
            team_ids: List of team UUIDs to remove

        Returns:
            Response data
        """
        data = {"team_ids": team_ids}
        return self.delete(f"/tournaments/{tournament_id}/teams", data)

    def finish_tournament(self, tournament_id: str, finished_by: str) -> Dict[str, Any]:
        """
        Finish a tournament

        Args:
            tournament_id: UUID of the tournament
            finished_by: UUID of the user finishing the tournament

        Returns:
            Updated tournament data
        """
        data = {"finished_by": finished_by}
        return self.post(f"/tournaments/{tournament_id}/finish", data)

    def delete_tournament(self, tournament_id: str) -> Dict[str, Any]:
        """
        Delete a tournament

        Args:
            tournament_id: UUID of the tournament

        Returns:
            Empty dict on success
        """
        return self.delete(f"/tournaments/{tournament_id}")
