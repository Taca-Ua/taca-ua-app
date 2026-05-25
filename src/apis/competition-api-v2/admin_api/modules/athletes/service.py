from dataclasses import dataclass
from typing import List, Optional

from admin_api.clients.modalities_service import StudentDTO, modalities_service_client


@dataclass
class _CourseSummary:
    id: str
    name: str
    abbreviation: str


@dataclass
class Athlete:
    id: str
    full_name: str
    course: _CourseSummary
    student_number: str
    is_member: bool

    # Optional metadata fields
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        # Ensure course is a _CourseSummary instance
        if isinstance(self.course, dict):
            self.course = _CourseSummary(**self.course)


@dataclass
class AthleteMembershipSyncResponse:
    participants_in_scope: int
    reset_to_non_socio: int
    set_as_socio: int
    unmatched_numbers: List[str]


class AthletesService:

    def _build_athlete_from_modalities_answer(
        self, athlete_data: StudentDTO
    ) -> Athlete:
        return Athlete(
            id=athlete_data.id,
            full_name=athlete_data.full_name,
            course=_CourseSummary(
                id=athlete_data.course.id,
                name=athlete_data.course.name,
                abbreviation=athlete_data.course.abbreviation,
            ),
            student_number=athlete_data.student_number,
            is_member=athlete_data.is_member,
        )

    def list_athletes(
        self,
        course_id: Optional[str] = None,
        team_id: Optional[str] = None,
        admin_id: Optional[str] = None,
    ) -> List[Athlete]:
        athletes_data = modalities_service_client.students.list_students(
            course_id=course_id,
            team_id=team_id,
            admin_id=admin_id,
        )

        return [
            self._build_athlete_from_modalities_answer(athlete_data)
            for athlete_data in athletes_data
        ]

    def create_student(
        self, full_name: str, course_id: str, student_number: str, is_member: bool
    ) -> Athlete:
        athlete_data = modalities_service_client.students.create_student(
            full_name=full_name,
            course_id=course_id,
            student_number=student_number,
            is_member=is_member,
        )

        return self._build_athlete_from_modalities_answer(athlete_data)

    def get_student(self, student_id: str) -> Athlete:
        athlete_data = modalities_service_client.students.get_student(student_id)

        return self._build_athlete_from_modalities_answer(athlete_data)

    def update_student(
        self,
        student_id: str,
        full_name: Optional[str] = None,
        course_id: Optional[str] = None,
        student_number: Optional[str] = None,
        is_member: Optional[bool] = None,
    ) -> Athlete:
        athlete_data = modalities_service_client.students.update_student(
            student_id,
            full_name=full_name,
            course_id=course_id,
            student_number=student_number,
            is_member=is_member,
        )

        return self._build_athlete_from_modalities_answer(athlete_data)

    def delete_student(self, student_id: str) -> None:
        modalities_service_client.students.delete_student(student_id)

    def sync_student_membership(
        self, student_numbers: List[str]
    ) -> AthleteMembershipSyncResponse:
        response = modalities_service_client.students.sync_student_membership(
            student_numbers
        )

        return AthleteMembershipSyncResponse(
            participants_in_scope=response["participants_in_scope"],
            reset_to_non_socio=response["reset_to_non_socio"],
            set_as_socio=response["set_as_socio"],
            unmatched_numbers=response["unmatched_numbers"],
        )


athletes_service = AthletesService()
