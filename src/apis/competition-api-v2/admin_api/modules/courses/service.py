"""
Courses management service
"""

from dataclasses import dataclass

from admin_api.clients.modalities_service import CourseDTO, modalities_service_client


@dataclass
class _NucleoSummary:
    id: str
    name: str
    abbreviation: str


@dataclass
class Course:
    id: str
    name: str
    abbreviation: str
    nucleo: _NucleoSummary
    belongs_to_season: bool


class CourseService:

    def _build_course_from_modalities_answer(self, data: CourseDTO) -> Course:
        return Course(
            id=data.id,
            name=data.name,
            abbreviation=data.abbreviation,
            nucleo=_NucleoSummary(
                id=data.nucleo.id,
                name=data.nucleo.name,
                abbreviation=data.nucleo.abbreviation,
            ),
            belongs_to_season=data.belongs_to_season,
        )

    def list_courses(self, admin_id: str = None, season_id: int = None) -> list[Course]:
        answer_data = modalities_service_client.courses.list_courses(
            admin_id=admin_id, season_id=season_id
        )

        return [
            self._build_course_from_modalities_answer(course) for course in answer_data
        ]

    def create_course(self, name: str, abbreviation: str, nucleo_id: str) -> Course:
        answer_data = modalities_service_client.courses.create_course(
            name=name, abbreviation=abbreviation, nucleo_id=nucleo_id
        )
        return self._build_course_from_modalities_answer(answer_data)

    def get_course(self, course_id: str, season_id: str = None) -> Course:
        answer_data = modalities_service_client.courses.get_course(
            course_id, season_id=season_id
        )
        return self._build_course_from_modalities_answer(answer_data)

    def update_course(
        self,
        course_id: str,
        name: str = None,
        abbreviation: str = None,
        nucleo_id: str = None,
    ) -> Course:
        answer_data = modalities_service_client.courses.update_course(
            course_id, name=name, abbreviation=abbreviation, nucleo_id=nucleo_id
        )
        return self._build_course_from_modalities_answer(answer_data)

    def add_to_season(self, course_id: str, season_id: int) -> Course:
        answer_data = modalities_service_client.courses.add_course_to_season(
            course_id, season_id
        )
        return self._build_course_from_modalities_answer(answer_data)

    def delete_course(self, course_id: str):
        modalities_service_client.courses.delete_course(course_id)


course_service = CourseService()
