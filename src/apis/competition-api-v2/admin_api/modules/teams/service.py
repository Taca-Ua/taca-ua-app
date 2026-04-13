from dataclasses import dataclass, field
from typing import List, Optional

from admin_api.clients.modalities_service import TeamDTO as ModalitiesTeamDTO
from admin_api.clients.modalities_service import modalities_service_client


@dataclass
class _CourseDTO:
    id: str
    name: str
    abbreviation: str


@dataclass
class _ModalityDTO:
    id: str
    name: str


@dataclass
class _PlayerDTO:
    id: str
    full_name: str
    student_number: str


@dataclass
class TeamDTO:
    id: str
    name: str
    modality: _ModalityDTO
    course: _CourseDTO
    players: Optional[List[_PlayerDTO]] = field(default_factory=list)


class TeamsService:

    def _build_team_from_modalities_response(
        self, team_data: ModalitiesTeamDTO, include_players: bool = False
    ) -> TeamDTO:

        obj = TeamDTO(
            id=team_data.id,
            name=team_data.name,
            modality=_ModalityDTO(
                id=team_data.modality.id,
                name=team_data.modality.name,
            ),
            course=_CourseDTO(
                id=team_data.course.id,
                name=team_data.course.name,
                abbreviation=team_data.course.abbreviation,
            ),
        )

        if include_players and team_data.players:
            obj.players = [
                _PlayerDTO(
                    id=player.id,
                    full_name=player.full_name,
                    student_number=player.student_number,
                )
                for player in team_data.players
            ]

        return obj

    def list_teams(self, admin_id=None, modality_id=None):
        teams_answer = modalities_service_client.teams.list_teams(
            admin_id=admin_id, modality_id=modality_id
        )
        return [
            self._build_team_from_modalities_response(team) for team in teams_answer
        ]

    def create_team(self, name, modality_id, course_id):
        team_answer = modalities_service_client.teams.create_team(
            name=name, modality_id=modality_id, course_id=course_id
        )
        return self._build_team_from_modalities_response(team_answer)

    def get_team(self, team_id):
        team_answer = modalities_service_client.teams.get_team(team_id)
        return self._build_team_from_modalities_response(
            team_answer, include_players=True
        )

    def update_team(
        self,
        team_id,
        name=None,
        modality_id=None,
        course_id=None,
        players_add=None,
        players_remove=None,
    ):
        team_answer = modalities_service_client.teams.update_team(
            team_id,
            name=name,
            modality_id=modality_id,
            course_id=course_id,
            players_add=players_add,
            players_remove=players_remove,
        )
        return self._build_team_from_modalities_response(
            team_answer, include_players=True
        )

    def delete_team(self, team_id):
        modalities_service_client.teams.delete_team(team_id)


teams_service = TeamsService()
