"""
Nucleos management service
"""

from dataclasses import dataclass, field
from typing import Optional

from admin_api.clients.minio_service import MinioService
from admin_api.clients.modalities_service import NucleoDTO, modalities_service_client
from django.core.files.images import ImageFile


@dataclass
class _NucleoCourse:
    id: str
    name: str
    abbreviation: str


@dataclass
class Nucleo:
    id: str
    name: str
    abbreviation: str
    logo_url: Optional[str] = None
    courses: list[_NucleoCourse] = field(default_factory=list)


class NucleosService:

    def __init__(self):
        self.minio_service = MinioService("nucleos-logos")

    def _build_nucleo_from_modalities_answer(self, data: NucleoDTO) -> Nucleo:

        return Nucleo(
            id=data.id,
            name=data.name,
            abbreviation=data.abbreviation,
            logo_url=data.logo_url,
            courses=[
                _NucleoCourse(
                    id=course.id, name=course.name, abbreviation=course.abbreviation
                )
                for course in data.courses
            ],
        )

    def list_nucleos(self, admin_id: Optional[str] = None) -> list[Nucleo]:
        answer_data = modalities_service_client.nucleos.list_nucleos(admin_id=admin_id)
        return [
            self._build_nucleo_from_modalities_answer(nucleo) for nucleo in answer_data
        ]

    def create_nucleo(
        self, name: str, abbreviation: str, image: ImageFile = None
    ) -> Nucleo:

        image_url = self.minio_service.upload_file(image) if image else None

        answer_data = modalities_service_client.nucleos.create_nucleo(
            name, abbreviation, image_url
        )
        return self._build_nucleo_from_modalities_answer(answer_data)

    def get_nucleo(self, nucleo_id) -> Nucleo:
        answer_data = modalities_service_client.nucleos.get_nucleo(nucleo_id)
        return self._build_nucleo_from_modalities_answer(answer_data)

    def update_nucleo(
        self, nucleo_id, name=None, abbreviation=None, image: ImageFile = None
    ) -> Nucleo:

        answer_data = modalities_service_client.nucleos.update_nucleo(
            nucleo_id, name, abbreviation
        )

        # If there is an image to update, we need to check if there is already a logo for this nucleo
        if image:
            if answer_data.logo_url is None:
                # If there is no logo, we just upload the new one and update the nucleo
                image_url = self.minio_service.upload_file(image)
                answer_data = modalities_service_client.nucleos.update_nucleo(
                    nucleo_id, name, abbreviation, image_url
                )
            else:
                # If there is already a logo, we update the existing one with the new image
                self.minio_service.update_file(answer_data.logo_url, image)

        return self._build_nucleo_from_modalities_answer(answer_data)

    def delete_nucleo(self, nucleo_id):
        # First we need to get the nucleo to check if there is a logo to delete from minio
        nucleo = self.get_nucleo(nucleo_id)
        if nucleo.logo_url:
            self.minio_service.delete_file(nucleo.logo_url)

        modalities_service_client.nucleos.delete_nucleo(nucleo_id)


nucleos_service = NucleosService()
