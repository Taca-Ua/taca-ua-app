"""
Modality management service
"""

from dataclasses import dataclass

from admin_api.clients.modalities_service import ModalityDTO, modalities_service_client


@dataclass
class _ModalityType:
    id: str
    name: str


@dataclass
class Modality:
    id: str
    name: str
    belongs_to_season: bool
    modality_type: _ModalityType


class ModalitiesService:
    def _build_modality_from_dto(self, dto: ModalityDTO) -> Modality:
        modality_type = (
            _ModalityType(
                id=dto.modality_type.id,
                name=dto.modality_type.name,
            )
            if dto.modality_type
            else None
        )

        return Modality(
            id=dto.id,
            name=dto.name,
            belongs_to_season=dto.belongs_to_season,
            modality_type=modality_type,
        )

    def list_modalities(self, season_id: str = None):
        answer = modalities_service_client.modalities.list_modalities(
            season_id=season_id
        )
        return [self._build_modality_from_dto(dto) for dto in answer]

    def create_modality(self, name: str, modality_type_id: str = None):
        answer = modalities_service_client.modalities.create_modality(
            name, modality_type_id
        )
        return self._build_modality_from_dto(answer)

    def get_modality(self, modality_id: str, season_id: str = None):
        answer = modalities_service_client.modalities.get_modality(
            modality_id, season_id=season_id
        )
        return self._build_modality_from_dto(answer)

    def update_modality(
        self, modality_id: str, name: str = None, modality_type_id: str = None
    ):
        answer = modalities_service_client.modalities.update_modality(
            modality_id, name, modality_type_id
        )
        return self._build_modality_from_dto(answer)

    def delete_modality(self, modality_id: str):
        modalities_service_client.modalities.delete_modality(modality_id)


modalities_service = ModalitiesService()
