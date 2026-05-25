from dataclasses import dataclass
from typing import List, Optional

from admin_api.clients.minio_service import MinioService
from admin_api.clients.modalities_service import (
    RegulationDTO,
    modalities_service_client,
)
from django.core.files.uploadedfile import UploadedFile


@dataclass
class Regulation:
    id: str
    title: str
    file_url: str
    description: Optional[str] = None


class RegulationsService:

    def __init__(self):
        self.minio_service_client = MinioService("regulations")

    def _build_regulation_from_dto(self, dto: RegulationDTO) -> Regulation:
        return Regulation(
            id=str(dto.id),
            title=dto.title,
            file_url=dto.file_url,
            description=dto.description,
        )

    def list_regulations(self, season_id: Optional[int] = None) -> List[Regulation]:
        regulations_answer = modalities_service_client.regulations.list_regulations(
            season_id=season_id
        )
        return [self._build_regulation_from_dto(dto) for dto in regulations_answer]

    def get_regulation(self, regulation_id: str) -> Regulation:
        regulation_dto = modalities_service_client.regulations.get_regulation(
            regulation_id
        )
        return self._build_regulation_from_dto(regulation_dto)

    def create_regulation(
        self,
        title: str,
        file: UploadedFile,
        description: Optional[str] = "",
        season_id: Optional[int] = None,
    ) -> Regulation:

        file_url = self.minio_service_client.upload_file(file)

        regulation_dto = (
            modalities_service_client.regulations.create_regulation_internal(
                title=title,
                file_url=file_url,
                description=description,
                season_id=season_id,
            )
        )

        return self._build_regulation_from_dto(regulation_dto)

    def update_regulation(
        self,
        regulation_id: str,
        file: Optional[UploadedFile] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Regulation:
        regulation_dto = modalities_service_client.regulations.update_regulation(
            regulation_id=regulation_id, title=title, description=description
        )

        if file:
            self.minio_service_client.update_file(regulation_dto.file_url, file)

        return self._build_regulation_from_dto(regulation_dto)

    def delete_regulation(self, regulation_id: str) -> None:
        file_to_delete = self.get_regulation(regulation_id).file_url
        modalities_service_client.regulations.delete_regulation(regulation_id)
        self.minio_service_client.delete_file(file_to_delete)


regulations_service = RegulationsService()
