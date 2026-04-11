"""
Matches management service
"""

from dataclasses import dataclass, field
from typing import List

from admin_api.clients.matches_service import MatchDTO, matches_service_client
from admin_api.modules.modalities.service import modalities_service_client


@dataclass
class Participant:
    participant_id: str
    name: str
    score: int
    position: int


@dataclass
class Match:
    id: str
    tournament_id: str
    location: str
    start_time: str
    status: str
    participants: List[Participant] = field(default_factory=list)


class MatchesService:
    """Service for managing matches"""

    def _build_match_from_dto(
        self, match_dto: MatchDTO, *, teams_info: dict = None, athlete_info: dict = None
    ) -> Match:
        """Helper method to convert MatchDTO to Match domain model"""
        if teams_info is None:
            teams_info = modalities_service_client.teams.get_teams_by_ids(
                [
                    participant.team_id
                    for participant in match_dto.participants
                    if participant.team_id is not None
                ]
            )

        if athlete_info is None:
            athlete_info = modalities_service_client.students.get_students_by_ids(
                [
                    participant.athlete_id
                    for participant in match_dto.participants
                    if participant.athlete_id is not None
                ]
            )

        participants = [
            Participant(
                participant_id=participant.id,
                name=(
                    teams_info.get(participant.team_id, {}).name
                    if participant.team_id
                    else (
                        athlete_info.get(participant.athlete_id, {}).name
                        if participant.athlete_id
                        else "Unknown Participant"
                    )
                ),
                score=participant.score if participant.score is not None else 0,
                position=(
                    participant.position if participant.position is not None else 0
                ),
            )
            for participant in match_dto.participants
        ]

        return Match(
            id=match_dto.id,
            tournament_id=match_dto.tournament_id,
            location=match_dto.location,
            start_time=match_dto.start_time,
            status=match_dto.status,
            participants=participants,
        )

    def list_matches(
        self, tournament_id: str = None, status: str = None
    ) -> List[Match]:
        """List matches, optionally filtered by tournament"""

        matches_data = matches_service_client.list_matches(
            tournament_id=tournament_id, status=status
        )

        teams_info = modalities_service_client.teams.get_teams_by_ids(
            [
                participant.team_id
                for match_dto in matches_data
                for participant in match_dto.participants
                if participant.team_id is not None
            ]
        )
        athlete_info = modalities_service_client.students.get_students_by_ids(
            [
                participant.athlete_id
                for match_dto in matches_data
                for participant in match_dto.participants
                if participant.athlete_id is not None
            ]
        )

        return [
            self._build_match_from_dto(
                match_dto, teams_info=teams_info, athlete_info=athlete_info
            )
            for match_dto in matches_data
        ]

    def create_match(
        self,
        tournament_id: str,
        location: str,
        start_time: str,
        participants_ids: List[str],
    ) -> Match:
        """Create a new match"""
        match_dto = matches_service_client.create_match(
            tournament_id=tournament_id,
            location=location,
            start_time=start_time,
            participants=participants_ids,
            created_by="00000000-0000-0000-0000-000000000000",  # Placeholder for created_by
        )
        return self._build_match_from_dto(match_dto)

    def get_match(self, match_id: str) -> Match:
        """Get match details by ID"""
        match_dto = matches_service_client.get_match(match_id=match_id)
        return self._build_match_from_dto(match_dto)

    def update_match(
        self,
        match_id: str,
        location: str = None,
        start_time: str = None,
        status: str = None,
    ) -> Match:
        """Update match metadata"""
        match_dto = matches_service_client.update_match(
            match_id=match_id,
            location=location,
            start_time=start_time,
            status=status,
            updated_by="00000000-0000-0000-0000-000000000000",  # Placeholder for updated_by
        )
        return self._build_match_from_dto(match_dto)

    def delete_match(self, match_id: str) -> None:
        """Delete a match"""
        matches_service_client.delete_match(
            match_id=match_id,
            deleted_by="00000000-0000-0000-0000-000000000000",  # Placeholder for deleted_by
        )

    def publish_match_results(self, match_id: str) -> Match:
        """Publish match results"""
        match_dto = matches_service_client.publish_match_results(
            match_id=match_id,
            published_by="00000000-0000-0000-0000-000000000000",  # Placeholder for published_by
        )
        return self._build_match_from_dto(match_dto)

    def assign_lineup(self, match_id: str, participant_ids: List[str]) -> Match:
        """Assign lineup to a match"""
        match_dto = matches_service_client.assign_lineup(
            match_id=match_id,
            participant_ids=participant_ids,
            assigned_by="00000000-0000-0000-0000-000000000000",  # Placeholder for assigned_by
        )
        return self._build_match_from_dto(match_dto)

    def add_comment(self, match_id: str, comment_text: str) -> Match:
        """Add a comment to a match"""
        match_dto = matches_service_client.add_comment(
            match_id=match_id,
            comment_text=comment_text,
            commented_by="00000000-0000-0000-0000-000000000000",  # Placeholder for commented_by
        )
        return self._build_match_from_dto(match_dto)

    def delete_comment(self, match_id: str, comment_id: str) -> Match:
        """Delete a comment from a match"""
        match_dto = matches_service_client.delete_comment(
            match_id=match_id,
            comment_id=comment_id,
            deleted_by="00000000-0000-0000-0000-000000000000",  # Placeholder for deleted_by
        )
        return self._build_match_from_dto(match_dto)

    def generate_match_report(self, match_id: str) -> bytes:
        """Generate a PDF report for a match"""
        raise NotImplementedError("Report generation is not implemented yet")

    def generate_match_team_report(self, match_id: str, team_id: str) -> bytes:
        """Generate a PDF report for a specific team in a match"""
        raise NotImplementedError("Team report generation is not implemented yet")


matches_service = MatchesService()
