from dataclasses import dataclass
from typing import List

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
    description: str
    is_playoff: bool
    escaloes: List[_Escalao]


class ModalityTypesService:

    def _build_admin_from_modalities_answer(
        self, modality: ModalityTypeDTO
    ) -> ModalityType:
        return ModalityType(
            id=modality.id,
            name=modality.name,
            description=modality.description,
            is_playoff=modality.is_playoff,
            escaloes=[
                _Escalao(
                    escalao=escalao.escalao,
                    maxParticipants=escalao.maxParticipants,
                    minParticipants=escalao.minParticipants,
                    points=escalao.points,
                )
                for escalao in modality.escaloes
            ],
        )

    def list_modality_types(self, include_playoff=False) -> List[ModalityType]:
        """List all modality types, optionally including playoff type

        Args:
            include_playoff (bool, optional): _description_. Defaults to False.
        """
        answer = modalities_service_client.modality_types.list_modality_types(
            include_playoff=include_playoff
        )
        return [
            self._build_admin_from_modalities_answer(modality) for modality in answer
        ]

    def create_modality_type(
        self, name, description="", escaloes=None, is_playoff=False
    ) -> List[ModalityType]:
        """Create a new modality type

        Args:
            name (str): Name of the modality type
            description (str, optional): Description of the modality type. Defaults to "".
            escaloes (list, optional): List of escaloes for the modality type. Defaults to None.
            is_playoff (bool, optional): Whether the modality type is a playoff. Defaults to False.
        """
        answer = modalities_service_client.modality_types.create_modality_type(
            name=name,
            description=description,
            escaloes=escaloes or [],
            is_playoff=is_playoff,
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
    ):
        """Update an existing modality type

        Args:
            modality_type_id (str): ID of the modality type to update
            name (str, optional): New name for the modality type. Defaults to None.
            description (str, optional): New description for the modality type. Defaults to None.
            escaloes (list, optional): New list of escaloes for the modality type. Defaults to None.
            is_playoff (bool, optional): Whether the modality type is a playoff. Defaults to None.
        """
        answer = modalities_service_client.modality_types.update_modality_type(
            modality_type_id=modality_type_id,
            name=name,
            description=description,
            escaloes=escaloes,
            is_playoff=is_playoff,
        )
        return self._build_admin_from_modalities_answer(answer)

    def delete_modality_type(self, modality_type_id):
        """Delete a modality type by ID

        Args:
            modality_type_id (str): ID of the modality type to delete
        """
        modalities_service_client.modality_types.delete_modality_type(modality_type_id)


modality_types_service = ModalityTypesService()
