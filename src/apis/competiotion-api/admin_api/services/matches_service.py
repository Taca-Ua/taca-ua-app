"""
Service for communicating with matches-service microservice
"""

import os
from typing import Any, Dict, List, Optional

from .base_service import BaseService


class MatchesService(BaseService):
    """Service for managing matches via matches-service"""

    def __init__(self):
        base_url = os.environ.get("MATCHES_SERVICE_URL", "http://matches-service:8000")
        super().__init__(base_url)

    def create_match(
        self,
        tournament_id: str,
        team_home_id: str,
        team_away_id: str,
        location: str,
        start_time: str,
        created_by: str,
    ) -> Dict[str, Any]:
        """
        Create a new match

        Args:
            tournament_id: UUID of the tournament
            team_home_id: UUID of the home team
            team_away_id: UUID of the away team
            location: Match location
            start_time: Start time (ISO 8601)
            created_by: UUID of the user creating

        Returns:
            Created match data
        """
        data = {
            "tournament_id": tournament_id,
            "team_home_id": team_home_id,
            "team_away_id": team_away_id,
            "location": location,
            "start_time": start_time,
            "created_by": created_by,
        }

        return self.post("/matches", data)

    def list_matches(
        self,
        tournament_id: Optional[str] = None,
        modality_id: Optional[str] = None,
        team_id: Optional[str] = None,
        course_id: Optional[str] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List matches with optional filters

        Args:
            tournament_id: Filter by tournament
            modality_id: Filter by modality
            team_id: Filter by team (home or away)
            course_id: Filter by course
            date: Filter by specific date (ISO 8601)
            date_from: Filter from date (ISO 8601)
            date_to: Filter to date (ISO 8601)
            status: Filter by status (scheduled, in_progress, finished, cancelled)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of matches
        """
        params = {"limit": limit, "offset": offset}

        if tournament_id:
            params["tournament_id"] = tournament_id
        if modality_id:
            params["modality_id"] = modality_id
        if team_id:
            params["team_id"] = team_id
        if course_id:
            params["course_id"] = course_id
        if date:
            params["date"] = date
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if status:
            params["status"] = status

        return self.get("/matches", params=params)

    def get_match(self, match_id: str) -> Dict[str, Any]:
        """
        Get match details including lineups and comments

        Args:
            match_id: UUID of the match

        Returns:
            Match data
        """
        return self.get(f"/matches/{match_id}")

    def update_match(
        self,
        match_id: str,
        updated_by: str,
        location: Optional[str] = None,
        start_time: Optional[str] = None,
        team_home_id: Optional[str] = None,
        team_away_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a match

        Args:
            match_id: UUID of the match
            updated_by: UUID of the user updating
            location: Optional new location
            start_time: Optional new start time
            team_home_id: Optional new home team
            team_away_id: Optional new away team

        Returns:
            Updated match data
        """
        data = {"updated_by": updated_by}

        if location is not None:
            data["location"] = location
        if start_time is not None:
            data["start_time"] = start_time
        if team_home_id is not None:
            data["team_home_id"] = team_home_id
        if team_away_id is not None:
            data["team_away_id"] = team_away_id

        return self.put(f"/matches/{match_id}", data)

    def register_result(
        self,
        match_id: str,
        home_score: int,
        away_score: int,
        registered_by: str,
        additional_details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register match result

        Args:
            match_id: UUID of the match
            home_score: Home team score
            away_score: Away team score
            registered_by: UUID of the user registering
            additional_details: Optional additional details (goals, cards, etc.)

        Returns:
            Updated match data
        """
        data = {
            "home_score": home_score,
            "away_score": away_score,
            "registered_by": registered_by,
        }

        if additional_details is not None:
            data["additional_details"] = additional_details

        return self.post(f"/matches/{match_id}/result", data)

    def assign_lineup(
        self, match_id: str, team_id: str, players: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assign lineup for a team in a match

        Args:
            match_id: UUID of the match
            team_id: UUID of the team
            players: List of player objects with player_id, jersey_number, is_starter

        Returns:
            Response data
        """
        data = {"team_id": team_id, "players": players}

        return self.post(f"/matches/{match_id}/lineup", data)

    def add_comment(
        self, match_id: str, message: str, author_id: str
    ) -> Dict[str, Any]:
        """
        Add comment to a match

        Args:
            match_id: UUID of the match
            message: Comment message
            author_id: UUID of the author

        Returns:
            Created comment data
        """
        data = {"message": message, "author_id": author_id}

        return self.post(f"/matches/{match_id}/comments", data)

    def get_match_sheet(self, match_id: str, format: str = "pdf") -> Dict[str, Any]:
        """
        Get match sheet (PDF or JSON)

        Args:
            match_id: UUID of the match
            format: Output format (pdf, json)

        Returns:
            Match sheet data or stream
        """
        params = {"format": format}
        return self.get(f"/matches/{match_id}/sheet", params=params)

    def delete_match(self, match_id: str) -> Dict[str, Any]:
        """
        Delete a match

        Args:
            match_id: UUID of the match

        Returns:
            Empty dict on success
        """
        return self.delete(f"/matches/{match_id}")
