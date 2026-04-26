"""
Nucleos management service
"""

from dataclasses import dataclass, field
from typing import Optional

from admin_api.clients.modalities_service import NucleoDTO, modalities_service_client


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
    courses: list[_NucleoCourse] = field(default_factory=list)


class NucleosService:

    def _build_nucleo_from_modalities_answer(self, data: NucleoDTO) -> Nucleo:

        return Nucleo(
            id=data.id,
            name=data.name,
            abbreviation=data.abbreviation,
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

    def create_nucleo(self, name, abbreviation) -> Nucleo:
        answer_data = modalities_service_client.nucleos.create_nucleo(
            name, abbreviation
        )
        return self._build_nucleo_from_modalities_answer(answer_data)

    def get_nucleo(self, nucleo_id) -> Nucleo:
        answer_data = modalities_service_client.nucleos.get_nucleo(nucleo_id)
        return self._build_nucleo_from_modalities_answer(answer_data)

    def update_nucleo(self, nucleo_id, name=None, abbreviation=None) -> Nucleo:
        answer_data = modalities_service_client.nucleos.update_nucleo(
            nucleo_id, name, abbreviation
        )
        return self._build_nucleo_from_modalities_answer(answer_data)

    def delete_nucleo(self, nucleo_id):
        modalities_service_client.nucleos.delete_nucleo(nucleo_id)


nucleos_service = NucleosService()
