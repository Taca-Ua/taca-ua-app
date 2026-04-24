"""
Matches management service
"""

from dataclasses import dataclass, field
from typing import Dict, List

from admin_api.clients.matches_service import MatchDTO, matches_service_client
from admin_api.clients.modalities_service import (
    StudentDTO,
    TeamDTO,
    modalities_service_client,
)
from admin_api.clients.tournaments_service import tournaments_service_client


@dataclass
class Participant:
    id: str
    entity_id: str
    name: str
    score: int
    position: int


@dataclass
class Comment:
    id: str
    message: str
    created_at: str


@dataclass
class LineupPlayer:
    player_id: str
    player_name: str
    player_course: str = None
    player_student_number: str = None
    is_starter: bool = None
    jersey_number: int = None


@dataclass
class Lineup:
    participant_id: str
    lineup: List[LineupPlayer] = field(default_factory=list)


@dataclass
class Match:
    id: str
    tournament_id: str
    location: str
    start_time: str
    status: str
    participants: List[Participant] = field(default_factory=list)
    comments: List[Comment] = field(default_factory=list)
    lineups: List[Lineup] = field(default_factory=list)


class MatchesService:
    """Service for managing matches"""

    def _build_multiple_matches_from_dtos(
        self, matches_dto: List[MatchDTO], include_details: bool = False
    ) -> List[Match]:

        # tournament phase
        tournament_ids = set(match_dto.tournament_id for match_dto in matches_dto)
        tournament_competitors_info: Dict[str, Dict[str, str]] = (
            {}
        )  # tournament -> competitor_id -> (competitor_type, competitor_entity_id)
        for tournament_id in tournament_ids:
            tournament_data = tournaments_service_client.get_tournament(tournament_id)

            tournament_competitors_info[tournament_id] = {}
            for competitor in tournament_data.competitors:
                tournament_competitors_info[tournament_id][competitor.id] = (
                    competitor.competitor_type,
                    competitor.competitor_entity_id,
                )

        # competitor info
        tournament_competitor_entities_info: Dict[tuple, TeamDTO | StudentDTO] = (
            {}
        )  # (competitor_type, competitor_entity_id) -> competitor_data
        teams_data = modalities_service_client.teams.get_teams_by_ids(
            [
                competitor_entity_id
                for tournament_id in tournament_ids
                for _, (
                    competitor_type,
                    competitor_entity_id,
                ) in tournament_competitors_info[tournament_id].items()
                if competitor_type == "team"
            ]
        )
        for team in teams_data:
            tournament_competitor_entities_info[("team", teams_data[team].id)] = (
                teams_data[team]
            )

        students_data = modalities_service_client.students.get_students_by_ids(
            [
                competitor_entity_id
                for tournament_id in tournament_ids
                for _, (
                    competitor_type,
                    competitor_entity_id,
                ) in tournament_competitors_info[tournament_id].items()
                if competitor_type == "athlete"
            ]
        )
        for student in students_data:
            tournament_competitor_entities_info[
                ("athlete", students_data[student].id)
            ] = students_data[student]

        resp_lineups = {}  # (match_id, participant_id) -> lineup details
        if include_details:
            # build with lineups player info
            all_player_ids = set()
            for match_dto in matches_dto:
                if not match_dto.lineups:
                    continue
                for lineup in match_dto.lineups:
                    for player in lineup.lineup:
                        all_player_ids.add(player.player_id)

            players_data = modalities_service_client.students.get_students_by_ids(
                list(all_player_ids)
            )

            for match_dto in matches_dto:
                if not match_dto.lineups:
                    continue
                for lineup in match_dto.lineups:
                    resp_lineups[(match_dto.id, lineup.participant_id)] = []
                    for player in lineup.lineup:
                        player_data = players_data.get(player.player_id)
                        if player_data:
                            resp_lineups[(match_dto.id, lineup.participant_id)].append(
                                LineupPlayer(
                                    player_id=player.player_id,
                                    player_name=player_data.full_name,
                                    player_course=player_data.course.name,
                                    player_student_number=player_data.student_number,
                                    is_starter=player.is_starter,
                                    jersey_number=player.jersey_number,
                                )
                            )

        # build matches
        resp = []
        for match_dto in matches_dto:
            # participants info
            participants = []
            for participant in match_dto.participants:
                entity_key = tournament_competitors_info[match_dto.tournament_id][
                    participant.participant
                ]
                entity_data = tournament_competitor_entities_info[entity_key]
                participants.append(
                    Participant(
                        id=participant.participant,
                        entity_id=entity_data.id,
                        name=(
                            entity_data.name
                            if isinstance(entity_data, TeamDTO)
                            else entity_data.full_name
                        ),
                        score=participant.score,
                        position=participant.position,
                    )
                )

            # build match
            resp.append(
                Match(
                    id=match_dto.id,
                    tournament_id=match_dto.tournament_id,
                    location=match_dto.location,
                    start_time=match_dto.start_time,
                    status=match_dto.status,
                    participants=participants,
                    comments=(
                        [
                            Comment(
                                id=comment.id,
                                message=comment.message,
                                created_at=comment.created_at,
                            )
                            for comment in match_dto.comments
                        ]
                        if include_details and match_dto.comments
                        else []
                    ),
                    lineups=(
                        [
                            Lineup(
                                participant_id=lineup.participant_id,
                                lineup=resp_lineups.get(
                                    (match_dto.id, lineup.participant_id), []
                                ),
                            )
                            for lineup in match_dto.lineups
                        ]
                        if not students_data
                        else None
                    ),  # Only include lineups if we have a team based match
                )
            )

        return resp

    def _build_match_from_dto(
        self, match_dto: MatchDTO, include_details: bool = False
    ) -> Match:
        """Helper method to convert MatchDTO to Match domain model"""
        matches = self._build_multiple_matches_from_dtos(
            [match_dto], include_details=include_details
        )
        return matches[0] if matches else None

    def list_matches(
        self, tournament_id: str = None, status: str = None
    ) -> List[Match]:
        """List matches, optionally filtered by tournament"""

        matches_data = matches_service_client.list_matches(
            tournament_id=tournament_id, status=status
        )

        return self._build_multiple_matches_from_dtos(matches_data)

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
        return self._build_match_from_dto(match_dto, include_details=True)

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
        return self._build_match_from_dto(match_dto, include_details=True)

    def delete_match(self, match_id: str) -> None:
        """Delete a match"""
        matches_service_client.delete_match(
            match_id=match_id,
        )

    def publish_match_results(
        self, match_id: str, participant_results: List[dict]
    ) -> Match:
        """Publish match results"""
        match_dto = matches_service_client.update_match_results(
            match_id=match_id,
            participant_results=participant_results,
            status="finished",  # Assuming publishing results also sets status to finished
        )
        return self._build_match_from_dto(match_dto, include_details=True)

    def assign_lineup(
        self, match_id: str, participant: str, players: List[str]
    ) -> Match:
        """Assign lineup to a match"""
        match_dto = matches_service_client.assign_lineup(
            match_id=match_id,
            participant=participant,
            players=players,
        )
        return self._build_match_from_dto(match_dto, include_details=True)

    def update_lineup(
        self, match_id: str, participant: str, players: List[dict]
    ) -> Match:
        """Update lineup of a match"""
        match_dto = matches_service_client.update_lineup(
            match_id=match_id,
            participant=participant,
            players=players,
        )
        return self._build_match_from_dto(match_dto, include_details=True)

    def add_comment(self, match_id: str, comment_text: str) -> Match:
        """Add a comment to a match"""
        match_dto = matches_service_client.add_comment(
            match_id=match_id,
            message=comment_text,
            created_by="00000000-0000-0000-0000-000000000000",  # Placeholder for commented_by
        )
        return self._build_match_from_dto(match_dto, include_details=True)

    def delete_comment(self, match_id: str, comment_id: str) -> Match:
        """Delete a comment from a match"""
        matches_service_client.delete_comment(
            match_id=match_id,
            comment_id=comment_id,
            # deleted_by="00000000-0000-0000-0000-000000000000",  # Placeholder for deleted_by
        )
        return

    def generate_match_report(self, match_id: str) -> bytes:
        """Generate a PDF report for a match"""
        raise NotImplementedError("Report generation is not implemented yet")

    def generate_match_team_report(self, match_id: str, team_id: str) -> bytes:
        """Generate a PDF report for a specific team in a match"""
        raise NotImplementedError("Team report generation is not implemented yet")


matches_service = MatchesService()
