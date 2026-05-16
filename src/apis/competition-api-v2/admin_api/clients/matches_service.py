"""
Service for communicating with matches-service microservice
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional
from uuid import UUID

from ..utils.base_service import BaseService


@dataclass
class MatchParticipantDTO:
    participant: UUID
    match_id: UUID
    # participant_type: str  # "team" or "athlete"
    # team_id: Optional[UUID] = None
    # athlete_id: Optional[UUID] = None
    score: Optional[int] = None
    position: Optional[int] = None
    result_metadata: Optional[Dict[str, Any]] = None


@dataclass
class MatchLineupPlayerDTO:
    player_id: UUID
    is_starter: Optional[bool] = None
    jersey_number: Optional[int] = None


@dataclass
class MatchLineupDTO:
    participant_id: UUID
    lineup: List[MatchLineupPlayerDTO] = field(default_factory=list)

    def __post_init__(self):
        self.lineup = [
            (
                MatchLineupPlayerDTO(**player)
                if not isinstance(player, MatchLineupPlayerDTO)
                else player
            )
            for player in self.lineup
        ]


@dataclass
class MatchDTO:
    id: UUID
    tournament_id: Optional[UUID]
    location: str
    start_time: str  # ISO format
    status: str  # "scheduled", "in_progress", "finished", "cancelled"
    created_by: UUID
    created_at: str  # ISO format
    updated_at: str  # ISO format
    participants: List[MatchParticipantDTO] = field(default_factory=list)
    comments: List["CommentDTO"] = field(default_factory=list)
    lineups: List["MatchLineupDTO"] = field(default_factory=list)

    def __post_init__(self):
        # Convert participants dicts to MatchParticipantDTO if necessary
        self.participants = [
            MatchParticipantDTO(**p) if not isinstance(p, MatchParticipantDTO) else p
            for p in self.participants
        ]

        self.comments = [
            CommentDTO(**c) if not isinstance(c, CommentDTO) else c
            for c in self.comments
        ]

        self.lineups = [
            MatchLineupDTO(**line) if not isinstance(line, MatchLineupDTO) else line
            for line in self.lineups
        ]


@dataclass
class LineupDTO:
    id: UUID
    match_id: UUID
    team_id: UUID
    player_id: UUID
    jersey_number: int
    is_starter: bool
    created_at: str  # ISO format


@dataclass
class CommentDTO:
    id: UUID
    # match_id: UUID
    message: str
    created_by: UUID
    created_at: str  # ISO format
    tournament_id: Optional[UUID] = None


@dataclass
class MatchesSummary:
    total_matches: int
    finished: int
    ongoing: int
    scheduled: int


class MatchesService(BaseService):
    """Service for managing matches via matches-service"""

    def __init__(self):
        base_url = os.environ.get("MATCHES_SERVICE_URL", "http://matches-service:8000")
        super().__init__(base_url)

    # Match CRUD operations
    def list_matches(
        self,
        tournament_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        athlete_id: Optional[UUID] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MatchDTO]:
        """
        List matches with optional filters.

        Args:
            tournament_id: Filter by tournament
            team_id: Filter by team participant
            athlete_id: Filter by athlete participant
            date: Filter by specific date (ISO format)
            date_from: Filter by start date (ISO format)
            date_to: Filter by end date (ISO format)
            status: Filter by status (scheduled, in_progress, finished, cancelled)
            limit: Number of results per page (default: 50, max: 100)
            offset: Pagination offset

        Returns:
            Dict with matches list, total count, limit, and offset
        """
        params = {}
        if tournament_id is not None:
            params["tournament_id"] = str(tournament_id)

        matches_data = self.get("/matches", params=params)
        matches = [MatchDTO(**match) for match in matches_data.get("matches", [])]
        return matches

    def list_matches_stream(
        self,
        tournament_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        athlete_id: Optional[UUID] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Generator[MatchDTO, None, None]:
        """
        Stream matches with optional filters.

        Args:
            tournament_id: Filter by tournament
            team_id: Filter by team participant
            athlete_id: Filter by athlete participant
            date: Filter by specific date (ISO format)
            date_from: Filter by start date (ISO format)
            date_to: Filter by end date (ISO format)
            status: Filter by status (scheduled, in_progress, finished, cancelled)

        Yields:
            MatchDTO objects one by one as they are received from the stream
        """
        params = {}
        if tournament_id is not None:
            params["tournament_id"] = str(tournament_id)

        for match_data in self.stream_sse("/matches/stream", params=params):
            yield MatchDTO(**match_data)

    def list_matches_lazy(
        self,
        tournament_id: Optional[UUID] = None,
        team_id: Optional[UUID] = None,
        athlete_id: Optional[UUID] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[MatchDTO]:
        matches = []
        for match in self.list_matches_stream(
            tournament_id=tournament_id,
            team_id=team_id,
            athlete_id=athlete_id,
            date=date,
            date_from=date_from,
            date_to=date_to,
            status=status,
        ):
            matches.append(match)

        return matches

    def create_match(
        self,
        location: str,
        start_time: str,
        created_by: UUID,
        tournament_id: Optional[UUID] = None,
        participants: Optional[List[Dict[str, Any]]] = None,
        journey: Optional[int] = None,
    ) -> MatchDTO:
        """
        Create a new match with participants.

        Args:
            location: Match location
            start_time: Match start time (ISO format)
            created_by: User who created the match
            tournament_id: Tournament reference (optional)
            participants: List of participants with:
                - participant_type (str): "team" or "athlete"
                - team_id (UUID, optional): Team ID if participant_type is "team"
                - athlete_id (UUID, optional): Athlete ID if participant_type is "athlete"
            journey: Journey number (optional)

        Returns:
            Created match data
        """
        data = {
            "location": location,
            "start_time": start_time,
            "created_by": str(created_by),
        }
        if tournament_id is not None:
            data["tournament_id"] = str(tournament_id)
        if participants is not None:
            data["participants"] = participants
        if journey is not None:
            data["journey"] = journey

        match_data = self.post("/matches", data=data)
        return MatchDTO(**match_data)

    def get_match(self, match_id: UUID) -> MatchDTO:
        """
        Get a match by ID.

        Args:
            match_id: Match UUID

        Returns:
            Match data with participants
        """
        match_data = self.get(f"/matches/{match_id}")
        return MatchDTO(**match_data)

    def update_match(
        self,
        match_id: UUID,
        location: Optional[str] = None,
        start_time: Optional[str] = None,
        status: Optional[str] = None,
    ) -> MatchDTO:
        """
        Update a match.

        Args:
            match_id: Match UUID
            location: New location
            start_time: New start time (ISO format)
            status: New status (scheduled, in_progress, finished, cancelled)

        Returns:
            Updated match data
        """
        data = {}
        if location is not None:
            data["location"] = location
        if start_time is not None:
            data["start_time"] = start_time
        if status is not None:
            data["status"] = status

        updated_match_data = self.put(f"/matches/{match_id}", data=data)
        return MatchDTO(**updated_match_data)

    def delete_match(self, match_id: UUID) -> Dict[str, Any]:
        """
        Delete a match.

        Args:
            match_id: Match UUID

        Returns:
            Empty dict on success
        """
        return self.delete(f"/matches/{match_id}")

    # Participant operations
    def add_participant(
        self,
        match_id: UUID,
        participant_type: str,
        team_id: Optional[UUID] = None,
        athlete_id: Optional[UUID] = None,
    ) -> MatchParticipantDTO:
        """
        Add a participant to a match.

        Args:
            match_id: Match UUID
            participant_type: "team" or "athlete"
            team_id: Team ID if participant_type is "team"
            athlete_id: Athlete ID if participant_type is "athlete"

        Returns:
            Created participant data
        """
        data = {"participant_type": participant_type}
        if team_id is not None:
            data["team_id"] = str(team_id)
        if athlete_id is not None:
            data["athlete_id"] = str(athlete_id)

        participant_data = self.post(f"/matches/{match_id}/participants", data=data)
        return MatchParticipantDTO(**participant_data)

    def update_participant_result(
        self,
        match_id: UUID,
        participant_id: UUID,
        score: Optional[int] = None,
        position: Optional[int] = None,
        result_metadata: Optional[Dict[str, Any]] = None,
    ) -> MatchParticipantDTO:
        """
        Update a participant's result.

        Args:
            match_id: Match UUID
            participant_id: Participant UUID
            score: Participant score
            position: Participant position/rank
            result_metadata: Additional result data

        Returns:
            Updated participant data
        """
        data = {"participant_id": str(participant_id)}
        if score is not None:
            data["score"] = score
        if position is not None:
            data["position"] = position
        if result_metadata is not None:
            data["result_metadata"] = result_metadata

        participant_data = self.put(
            f"/matches/{match_id}/participants/{participant_id}", data=data
        )
        return MatchParticipantDTO(**participant_data)

    def remove_participant(
        self, match_id: UUID, participant_id: UUID
    ) -> Dict[str, Any]:
        """
        Remove a participant from a match.

        Args:
            match_id: Match UUID
            participant_id: Participant UUID

        Returns:
            Empty dict on success
        """
        return self.delete(f"/matches/{match_id}/participants/{participant_id}")

    # Lineup operations
    def assign_lineup(
        self,
        match_id: UUID,
        participant: UUID,
        players: List[Dict[str, Any]],
    ) -> MatchDTO:
        """
        Assign lineup for a team in a match.

        Args:
            match_id: Match UUID
            participant: Participant ID
            players: List of players with:
                - player_id (UUID/str): Player ID
                - jersey_number (int): Jersey number
                - is_starter (bool, optional): Whether player is starter (default: True)

        Returns:
            Success message with player count
        """
        data = {
            "participant": str(participant),
            "players": players,
        }
        match_data = self.post(f"/matches/{match_id}/lineup", data=data)
        return MatchDTO(**match_data)

    def get_lineup(
        self,
        match_id: UUID,
        team_id: Optional[UUID] = None,
    ) -> List[LineupDTO]:
        """
        Get lineup for a match.

        Args:
            match_id: Match UUID
            team_id: Filter by team (optional)

        Returns:
            List of lineup entries
        """
        params = {}
        if team_id is not None:
            params["team_id"] = str(team_id)

        lineup_data = self.get(f"/matches/{match_id}/lineup", params=params)
        return [LineupDTO(**entry) for entry in lineup_data]

    def update_lineup(
        self,
        match_id: UUID,
        participant: UUID,
        players: List[Dict[str, Any]],
    ) -> MatchDTO:
        """
        Update lineup for a team in a match.

        Args:
            match_id: Match UUID
            participant: Participant ID
            players: List of players with:
                - player_id (UUID/str): Player ID
                - jersey_number (int): Jersey number
                - is_starter (bool, optional): Whether player is starter (default: True)

        Returns:
            Updated match data with new lineup
        """
        data = {
            "participant": str(participant),
            "players": players,
        }
        match_data = self.put(f"/matches/{match_id}/lineup", data=data)
        return MatchDTO(**match_data)

    # Comment operations
    def add_comment(
        self,
        match_id: UUID,
        message: str,
        created_by: UUID,
    ) -> CommentDTO:
        """
        Add a comment to a match.

        Args:
            match_id: Match UUID
            message: Comment message
            created_by: User who created the comment

        Returns:
            Created comment data
        """
        data = {
            "message": message,
            "created_by": str(created_by),
        }

        comment_data = self.post(f"/matches/{match_id}/comments", data=data)
        return MatchDTO(**comment_data)

    def get_comments(self, match_id: UUID) -> List[CommentDTO]:
        """
        Get all comments for a match.

        Args:
            match_id: Match UUID

        Returns:
            List of comments
        """
        comments_data = self.get(f"/matches/{match_id}/comments")
        return [CommentDTO(**entry) for entry in comments_data]

    def delete_comment(
        self, match_id: UUID, comment_id: UUID, admin_id_check: UUID = None
    ) -> Dict[str, Any]:
        """
        Delete a comment.

        Args:
            match_id: Match UUID
            comment_id: Comment UUID
            admin_id_check: Admin ID to check if they have permission to delete the comment (optional)

        Returns:
            Empty dict on success
        """
        params = {}
        if admin_id_check is not None:
            params["admin_id_check"] = str(admin_id_check)
        return self.delete(f"/matches/{match_id}/comments/{comment_id}", params=params)

    # Batch result update
    def update_match_results(
        self,
        match_id: UUID,
        participant_results: List[Dict[str, Any]],
        status: Optional[str] = "finished",
    ) -> MatchDTO:
        """
        Update results for multiple participants and optionally finish the match.

        Args:
            match_id: Match UUID
            participant_results: List of participant results with:
                - participant_id (UUID): Participant ID
                - score (int, optional): Score
                - position (int, optional): Position/rank
                - result_metadata (Dict, optional): Additional metadata
            status: New match status (default: "finished")

        Returns:
            Updated match data with all participants
        """
        data = {"participant_results": participant_results}
        if status is not None:
            data["status"] = status

        match_data = self.put(f"/matches/{match_id}/results", data=data)
        return MatchDTO(**match_data)

    def get_matches_summary(
        self,
        tournaments_ids: Optional[List[UUID]] = None,
        tournaments_distribution: Optional[dict[UUID, List[UUID]]] = None,
    ) -> MatchesSummary:
        """
        Get summary information about matches, optionally filtered by tournament.

        Args:
            tournaments_ids: List of tournament UUIDs to filter by (optional)
            tournaments_distribution: Dict mapping tournament UUIDs to lists of competitor UUIDs (optional)

        Returns:
            Summary data with total matches, matches by status, and optionally matches by tournament
        """

        data = {
            "tournaments_ids": (
                [str(id) for id in tournaments_ids]
                if tournaments_ids is not None
                else None
            ),
            "tournaments_distribution": tournaments_distribution,
        }

        summary_data = self.post("/matches/summary", data=data)
        return MatchesSummary(**summary_data)


# Singleton instance
matches_service_client = MatchesService()
