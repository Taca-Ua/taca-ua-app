"""
Service for communicating with tournaments-service microservice
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..utils.base_service import BaseService


@dataclass
class CompetitorDTO:
    id: UUID
    tournament_id: UUID
    competitor_type: str  # "team" or "athlete"
    competitor: Dict[str, UUID]  # {"team_id": UUID} or {"athlete_id": UUID}
    competitor_entity_id: UUID  # ID of the team or athlete entity
    created_at: str  # ISO formatted datetime string


@dataclass
class _TournamentRankingPositionDTO:
    # id: UUID
    # tournament_id: UUID
    competitor_id: UUID
    position: int
    # created_at: str  # ISO formatted datetime string


@dataclass
class TournamentDTO:
    id: UUID
    name: str
    status: str  # "draft", "active", "finished"
    modality_id: UUID
    scoring_format_id: UUID
    competitor_type: str  # "team" or "athlete"
    season_id: int
    start_date: Optional[str] = None  # ISO formatted datetime string
    competitors: List[CompetitorDTO] = field(default_factory=list)
    ranking_positions: List[_TournamentRankingPositionDTO] = field(default_factory=list)
    format: str = "free"
    format_data: Optional[dict] = None  # Additional data for specific formats

    created_by: Optional[UUID] = None
    created_at: Optional[str] = None  # ISO formatted datetime string
    updated_at: Optional[str] = None  # ISO formatted datetime string
    finished_at: Optional[str] = None  # ISO formatted datetime string
    finished_by: Optional[UUID] = None

    def __post_init__(self):
        self.competitors = [
            CompetitorDTO(**competitor) for competitor in self.competitors
        ]
        self.ranking_positions = (
            [
                _TournamentRankingPositionDTO(**position)
                for position in self.ranking_positions
            ]
            if self.ranking_positions
            else []
        )


@dataclass
class TournamentSeasonSummary:
    @dataclass
    class _TournamentsDistribution:
        tournament_id: UUID
        competitors_ids: List[UUID]

        def __post_init__(self):
            if isinstance(self.competitors_ids, list):
                self.competitors_ids = [UUID(str(cid)) for cid in self.competitors_ids]

    tournaments_finished: int
    tournaments_ongoing: int
    tournaments_scheduled: int

    tournaments_ids: List[UUID]  # List of tournament IDs in the season
    competitors_distribution: List[_TournamentsDistribution] = None

    def __post_init__(self):
        if self.competitors_distribution is None:
            self.competitors_distribution = []

        if isinstance(self.competitors_distribution, list):
            self.competitors_distribution = [
                self._TournamentsDistribution(**entry)
                for entry in self.competitors_distribution
            ]


class TournamentsService(BaseService):
    """Service for managing tournaments via tournaments-service"""

    def __init__(self):
        base_url = os.environ.get(
            "TOURNAMENTS_SERVICE_URL", "http://tournaments-service:8000"
        )
        super().__init__(base_url)

    def list_tournaments(
        self,
        status_filter: Optional[str] = None,
        modality_id: Optional[UUID] = None,
        season_id: Optional[int] = None,
    ) -> List[TournamentDTO]:
        """
        List all tournaments with optional filters

        Args:
            status_filter: Filter by status (draft, active, finished)
            modality_id: Filter by modality ID
            season_id: Filter by season ID

        Returns:
            List of tournament dictionaries
        """
        params = {}
        if status_filter:
            params["status_filter"] = status_filter
        if modality_id:
            params["modality_id"] = str(modality_id)
        if season_id:
            params["season_id"] = season_id

        tournaments_data = self.get("/tournaments", params=params)
        return [TournamentDTO(**tournament) for tournament in tournaments_data]

    def get_tournament(self, tournament_id: UUID) -> TournamentDTO:
        """
        Get a tournament by ID

        Args:
            tournament_id: Tournament ID

        Returns:
            Tournament dictionary
        """
        tournament_data = self.get(f"/tournaments/{tournament_id}")
        return TournamentDTO(**tournament_data)

    def create_tournament(
        self,
        modality_id: UUID,
        name: str,
        scoring_format_id: UUID,
        competitor_type: str,
        season_id: int = None,
        start_date: Optional[str] = None,
        format: Optional[str] = None,
        format_data: Optional[dict] = None,
    ) -> TournamentDTO:
        """
        Create a new tournament

        Args:
            modality_id: ID of the modality
            name: Tournament name
            scoring_format_id: ID of the scoring format (regular vs playoff)
            competitor_type: "team" or "athlete"
            season_id: Season ID
            start_date: Optional start date (ISO format)
            format: Optional tournament format (e.g. "free", "round_robin", "single_elimination")
            format_data: Optional additional data for specific formats (e.g. number of groups for round

        Returns:
            Created tournament dictionary
        """
        data = {
            "modality_id": str(modality_id),
            "name": name,
            "scoring_format_id": str(scoring_format_id),
            "competitor_type": competitor_type,
            "season_id": season_id,
        }
        if start_date:
            data["start_date"] = start_date
        if format:
            data["format"] = format
        if format_data:
            data["format_data"] = format_data

        tournament_data = self.post("/tournaments", data=data)
        return TournamentDTO(**tournament_data)

    def update_tournament(
        self,
        tournament_id: UUID,
        name: Optional[str] = None,
        start_date: Optional[str] = None,
        status: Optional[str] = None,
        scoring_format_id: Optional[UUID] = None,
    ) -> TournamentDTO:
        """
        Update a tournament

        Args:
            tournament_id: Tournament ID
            name: New tournament name
            start_date: New start date (ISO format)
            status: New status (draft, active, finished)
            scoring_format_id: ID of the scoring format (regular vs playoff)
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
        if scoring_format_id is not None:
            data["scoring_format_id"] = str(scoring_format_id)

        tournament_data = self.put(f"/tournaments/{tournament_id}", data=data)
        return TournamentDTO(**tournament_data)

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
    ) -> TournamentDTO:
        """
        Mark a tournament as finished and set final rankings

        Args:
            tournament_id: Tournament ID
            ranking_entries: List of dicts with competitor_id and position
            finished_by: ID of the user finishing the tournament

        Returns:
            Updated tournament dictionary
        """
        data = {
            "ranking_entries": ranking_entries,
            "finished_by": str(finished_by),
        }

        tournament_data = self.post(f"/tournaments/{tournament_id}/finish", data=data)
        return TournamentDTO(**tournament_data)

    def add_competitors(
        self, tournament_id: UUID, competitors_data: List[Dict[str, Any]]
    ) -> TournamentDTO:
        """
        Add competitors to a tournament

        Args:
            tournament_id: Tournament ID
            competitors_data: List of competitor data dicts

        Returns:
            Updated tournament dictionary
        """
        tournament_data = self.put(
            f"/tournaments/{tournament_id}/competitors/add", data=competitors_data
        )
        return TournamentDTO(**tournament_data)

    def remove_competitors(
        self, tournament_id: UUID, competitors_ids: List[UUID]
    ) -> TournamentDTO:
        """
        Remove competitors from a tournament

        Args:
            tournament_id: Tournament ID
            competitors_ids: List of competitor IDs to remove

        Returns:
            Updated tournament dictionary
        """
        data = [str(competitor_id) for competitor_id in competitors_ids]

        tournament_data = self.put(
            f"/tournaments/{tournament_id}/competitors/remove", data=data
        )
        return TournamentDTO(**tournament_data)

    def get_tournaments_summary(
        self,
        season_id: int,
        teams_ids: List[UUID] = None,
        athletes_ids: List[UUID] = None,
    ) -> TournamentSeasonSummary:
        """
        Get summary information for all tournaments in a season

        Args:
            season_id: Season ID
            teams_ids: Optional list of team IDs to filter the summary
            athletes_ids: Optional list of athlete IDs to filter the summary

        Returns:
            Tournament season summary dictionary
        """
        data = {"season_id": season_id}

        if teams_ids is not None:
            data["teams_ids"] = [str(team_id) for team_id in teams_ids]

        if athletes_ids is not None:
            data["athletes_ids"] = [str(athlete_id) for athlete_id in athletes_ids]

        summary_data = self.post("/tournaments/summary", data=data)
        return TournamentSeasonSummary(
            tournaments_finished=summary_data.get("tournaments_finished", 0),
            tournaments_ongoing=summary_data.get("tournaments_ongoing", 0),
            tournaments_scheduled=summary_data.get("tournaments_scheduled", 0),
            tournaments_ids=summary_data.get("tournaments_ids", []),
            competitors_distribution=summary_data.get("competitors_distribution", []),
        )


# Singleton instance
tournaments_service_client = TournamentsService()
