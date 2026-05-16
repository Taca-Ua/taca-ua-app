from dataclasses import dataclass
from typing import List, Literal

from admin_api.clients.modalities_service import (
    ModalityTypeDTO,
    modalities_service_client,
)


@dataclass
class _Escalao:
    escalao: str
    maxParticipants: int
    minParticipants: int
    points: List[int]


@dataclass
class ModalityType:
    id: str
    name: str
    mode: str
    description: str
    num_escaloes: int
    escaloes: List[_Escalao]
    tournament_competitor_type: str


class ModalityTypesService:

    def _build_admin_from_modalities_answer(
        self, modality: ModalityTypeDTO
    ) -> ModalityType:
        return ModalityType(
            id=modality.id,
            name=modality.name,
            mode=modality.mode,
            description=modality.description,
            num_escaloes=len(modality.escaloes),
            escaloes=[
                _Escalao(
                    escalao=escalao.escalao,
                    maxParticipants=escalao.maxParticipants,
                    minParticipants=escalao.minParticipants,
                    points=escalao.points,
                )
                for escalao in modality.escaloes
            ],
            tournament_competitor_type=modality.tournament_competitor_type,
        )

    def list_modality_types(self, season_id=None, mode=None) -> List[ModalityType]:
        """List all modality types, optionally including playoff type

        Args:
            season_id (str, optional): ID of the season for which to list modality types. Defaults to None.
            mode (str, optional): Mode of the modality types to list. Defaults to None.
        """
        answer = modalities_service_client.modality_types.list_modality_types(
            season_id=season_id, mode=mode
        )
        return [
            self._build_admin_from_modalities_answer(modality) for modality in answer
        ]

    def create_modality_type(
        self,
        name: str,
        mode: Literal["modality", "points"],
        description: str = "",
        escaloes: list = None,
        tournament_competitor_type: Literal["individual", "team"] = None,
        season_id: int = None,
    ) -> List[ModalityType]:
        """Create a new modality type

        Args:
            name (str): Name of the modality type
            mode (str): Mode of the modality type, either "modality" or "points"
            description (str, optional): Description of the modality type. Defaults to "".
            escaloes (list, optional): List of escaloes for the modality type. Defaults to None.
            tournament_competitor_type (str, optional): Type of competitors in the tournament, either "individual" or "team".
            season_id (int, optional): ID of the season to which the modality type belongs. Defaults to None.
        """
        answer = modalities_service_client.modality_types.create_modality_type(
            name=name,
            description=description,
            escaloes=escaloes or [],
            mode=mode,
            tournament_competitor_type=tournament_competitor_type,
            season_id=season_id,
        )
        return self._build_admin_from_modalities_answer(answer)

    def get_modality_type(self, modality_type_id):
        """Get details of a modality type by ID

        Args:
            modality_type_id (str): ID of the modality type to retrieve
        """
        answer = modalities_service_client.modality_types.get_modality_type(
            modality_type_id
        )
        return self._build_admin_from_modalities_answer(answer)

    def update_modality_type(
        self,
        modality_type_id,
        name=None,
        description=None,
        escaloes=None,
        is_playoff=None,
        tournament_competitor_type=None,
    ):
        """Update an existing modality type

        Args:
            modality_type_id (str): ID of the modality type to update
            name (str, optional): New name for the modality type. Defaults to None.
            description (str, optional): New description for the modality type. Defaults to None.
            escaloes (list, optional): New list of escaloes for the modality type. Defaults to None.
            is_playoff (bool, optional): Whether the modality type is a playoff. Defaults to None.
            tournament_competitor_type (str, optional): Type of competitors in the tournament. Defaults to None.
        """
        answer = modalities_service_client.modality_types.update_modality_type(
            modality_type_id=modality_type_id,
            name=name,
            description=description,
            escaloes=escaloes,
            is_playoff=is_playoff,
            tournament_competitor_type=tournament_competitor_type,
        )
        return self._build_admin_from_modalities_answer(answer)

    def delete_modality_type(self, modality_type_id):
        """Delete a modality type by ID

        Args:
            modality_type_id (str): ID of the modality type to delete
        """
        modalities_service_client.modality_types.delete_modality_type(modality_type_id)


modality_types_service = ModalityTypesService()
