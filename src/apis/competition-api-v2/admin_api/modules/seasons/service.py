"""
Seasons management service
"""

from dataclasses import dataclass

from admin_api.clients.modalities_service import SeasonDTO, modalities_service_client


@dataclass
class Season:
    id: int
    name: str


class SeasonService:

    def _build_season_from_dto(self, dto: SeasonDTO) -> Season:
        return Season(id=dto.id, name=dto.name)

    def list_seasons(self) -> list[Season]:
        # Dummy implementation, replace with actual logic to fetch seasons
        season_dtos = modalities_service_client.seasons.list_seasons()
        return [self._build_season_from_dto(dto) for dto in season_dtos]

    def create_season(self, name: str, admin_id: str) -> Season:
        new_season_dto = modalities_service_client.seasons.create_season(
            name=name, created_by=admin_id
        )
        return self._build_season_from_dto(new_season_dto)

    def get_current_season(self) -> Season | None:
        current_season_dto = modalities_service_client.seasons.get_current_season()
        if not current_season_dto:
            return None
        return self._build_season_from_dto(current_season_dto)


seasons_service = SeasonService()
