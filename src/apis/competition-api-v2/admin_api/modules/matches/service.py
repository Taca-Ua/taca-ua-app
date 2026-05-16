"""
Matches management service
"""

from dataclasses import dataclass, field
from typing import Dict, List

from admin_api.clients.keycloak_service import keycloak_service_client
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
    author_name: str
    can_edit: bool
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

    def _fill_lineup_players_info(
        self,
        matches_dto: List[MatchDTO],
        matches_index: Dict[str, Match],
        admin_id: str,
    ) -> None:
        """Helper method to fill lineup players info in matches in place"""
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

        teams_ids_i_am_allowed_to_see = set(
            map(
                str,
                modalities_service_client.teams.list_teams_by_admin(admin_id=admin_id),
            )
        )

        for match_dto in matches_dto:
            matches_index[match_dto.id].lineups = []
            if not match_dto.lineups:
                continue
            for lineup in match_dto.lineups:
                lineup_players = []

                # If admin_id is None, we can assume it's a superadmin who can see all lineups, so we skip the check
                if admin_id is not None:
                    participant = next(
                        (
                            p
                            for p in matches_index[match_dto.id].participants
                            if p.id == lineup.participant_id
                        ),
                        None,
                    )
                    if participant.entity_id not in teams_ids_i_am_allowed_to_see:
                        matches_index[match_dto.id].lineups.append(
                            Lineup(participant_id=lineup.participant_id, lineup=None)
                        )
                        continue

                for player in lineup.lineup:
                    player_data = players_data.get(player.player_id)
                    if player_data:
                        lineup_players.append(
                            LineupPlayer(
                                player_id=player.player_id,
                                player_name=player_data.full_name,
                                player_course=player_data.course.name,
                                player_student_number=player_data.student_number,
                                is_starter=player.is_starter,
                                jersey_number=player.jersey_number,
                            )
                        )
                matches_index[match_dto.id].lineups.append(
                    Lineup(participant_id=lineup.participant_id, lineup=lineup_players)
                )

    def _fill_comments_info(
        self,
        matches_dto: List[MatchDTO],
        matches_index: Dict[str, Match],
        admin_id: str,
    ) -> Dict[str, List[Comment]]:
        """Helper method to fill comments info in matches in place"""
        comments_ids = set()
        for match_dto in matches_dto:
            if match_dto.comments:
                for comment in match_dto.comments:
                    comments_ids.add(comment.created_by)

        all_users = keycloak_service_client.get_multiple_admins(comments_ids)
        users_to_names = {
            user_id: user.first_name + " " + user.last_name
            for user_id, user in all_users.items()
        }
        for match_dto in matches_dto:
            if not match_dto.comments:
                continue
            matches_index[match_dto.id].comments = [
                Comment(
                    id=comment.id,
                    message=comment.message,
                    author_name=users_to_names.get(comment.created_by, "Unknown"),
                    created_at=comment.created_at,
                    can_edit=(
                        admin_id is None
                        or comment.created_by == admin_id
                        or "general_admin" in all_users.get(admin_id, {}).roles
                    ),  # If admin_id is None, we can assume it's a superadmin who can edit all comments
                )
                for comment in match_dto.comments
            ]

    def _build_multiple_matches_from_dtos(
        self,
        matches_dto: List[MatchDTO],
        include_details: bool = False,
        admin_id: str = None,
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
            ],
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

            # build matches

        # build basic match info
        resp: List[Match] = []
        matches_index: Dict[str, Match] = (
            {}
        )  # match_id -> match_obj in resp list, to be used later for adding lineups if include_details is True
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
            resp_match = Match(
                id=match_dto.id,
                tournament_id=match_dto.tournament_id,
                location=match_dto.location,
                start_time=match_dto.start_time,
                status=match_dto.status,
                participants=participants,
                comments=None,  # to be filled later if include_details is True
                lineups=None,  # to be filled later if include_details is True
            )
            resp.append(resp_match)
            matches_index[match_dto.id] = resp_match

        if include_details:
            self._fill_lineup_players_info(matches_dto, matches_index, admin_id)
            self._fill_comments_info(matches_dto, matches_index, admin_id)
        return resp

    def _build_match_from_dto(
        self, match_dto: MatchDTO, include_details: bool = False, admin_id: str = None
    ) -> Match:
        """Helper method to convert MatchDTO to Match domain model"""
        matches = self._build_multiple_matches_from_dtos(
            [match_dto], include_details=include_details, admin_id=admin_id
        )
        return matches[0] if matches else None

    def list_matches(
        self, tournament_id: str = None, status: str = None
    ) -> List[Match]:
        """List matches, optionally filtered by tournament"""

        matches_data = matches_service_client.list_matches_lazy(
            tournament_id=tournament_id, status=status
        )

        return self._build_multiple_matches_from_dtos(matches_data)

    def create_match(
        self,
        tournament_id: str,
        location: str,
        start_time: str,
        participants_ids: List[str],
        journey: int = None,
    ) -> Match:
        """Create a new match"""
        match_dto = matches_service_client.create_match(
            tournament_id=tournament_id,
            location=location,
            start_time=start_time,
            participants=participants_ids,
            journey=journey,
            created_by="00000000-0000-0000-0000-000000000000",  # Placeholder for created_by
        )
        return self._build_match_from_dto(match_dto)

    def get_match(self, match_id: str, admin_id: str = None) -> Match:
        """Get match details by ID"""
        match_dto = matches_service_client.get_match(match_id=match_id)
        return self._build_match_from_dto(
            match_dto, include_details=True, admin_id=admin_id
        )

    def update_match(
        self,
        match_id: str,
        location: str = None,
        start_time: str = None,
        status: str = None,
        admin_id: str = None,
    ) -> Match:
        """Update match metadata"""
        match_dto = matches_service_client.update_match(
            match_id=match_id,
            location=location,
            start_time=start_time,
            status=status,
        )
        return self._build_match_from_dto(
            match_dto, include_details=True, admin_id=admin_id
        )

    def delete_match(self, match_id: str) -> None:
        """Delete a match"""
        matches_service_client.delete_match(
            match_id=match_id,
        )

    def publish_match_results(
        self, match_id: str, participant_results: List[dict], admin_id: str = None
    ) -> Match:
        """Publish match results"""
        match_dto = matches_service_client.update_match_results(
            match_id=match_id,
            participant_results=participant_results,
            status="finished",  # Assuming publishing results also sets status to finished
        )
        return self._build_match_from_dto(
            match_dto, include_details=True, admin_id=admin_id
        )

    def assign_lineup(
        self, match_id: str, participant: str, players: List[str], admin_id: str = None
    ) -> Match:
        """Assign lineup to a match"""
        match_dto = matches_service_client.assign_lineup(
            match_id=match_id,
            participant=participant,
            players=players,
        )
        return self._build_match_from_dto(
            match_dto, include_details=True, admin_id=admin_id
        )

    def update_lineup(
        self, match_id: str, participant: str, players: List[dict], admin_id: str = None
    ) -> Match:
        """Update lineup of a match"""
        match_dto = matches_service_client.update_lineup(
            match_id=match_id,
            participant=participant,
            players=players,
        )
        return self._build_match_from_dto(
            match_dto, include_details=True, admin_id=admin_id
        )

    def add_comment(
        self, match_id: str, comment_text: str, admin_id: str = None
    ) -> Match:
        """Add a comment to a match"""
        match_dto = matches_service_client.add_comment(
            match_id=match_id,
            message=comment_text,
            created_by=admin_id
            or "00000000-0000-0000-0000-000000000000",  # Placeholder for created_by if admin_id is not provided
        )
        return self._build_match_from_dto(
            match_dto, include_details=True, admin_id=admin_id
        )

    def delete_comment(
        self, match_id: str, comment_id: str, admin_id: str = None
    ) -> None:
        """Delete a comment from a match"""
        matches_service_client.delete_comment(
            match_id=match_id,
            comment_id=comment_id,
            admin_id_check=admin_id,
            # deleted_by="00000000-0000-0000-0000-000000000000",  # Placeholder for deleted_by
        )
        return


matches_service = MatchesService()
