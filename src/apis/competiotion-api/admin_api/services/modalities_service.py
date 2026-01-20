"""
Service for communicating with modalities-service microservice
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID

from .base_service import BaseService


# DTOs
@dataclass
class NucleoDTO:
    id: UUID
    name: str
    abbreviation: str
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class CourseDTO:
    id: UUID
    name: str
    abbreviation: str
    nucleo: NucleoDTO
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.nucleo, NucleoDTO):
            self.nucleo = NucleoDTO(**self.nucleo)


@dataclass
class _EscalaDTO:
    escalao: str
    points: List[int] = field(default_factory=list)
    minParticipants: Optional[int] = None
    maxParticipants: Optional[int] = None


@dataclass
class ModalityTypeDTO:
    id: UUID
    name: str
    description: str
    escaloes: List[_EscalaDTO]
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        self.escaloes = [
            escalao if isinstance(escalao, _EscalaDTO) else _EscalaDTO(**escalao)
            for escalao in self.escaloes
        ]


@dataclass
class ModalityDTO:
    id: UUID
    name: str
    modality_type: ModalityTypeDTO
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.modality_type, ModalityTypeDTO):
            self.modality_type = ModalityTypeDTO(**self.modality_type)


@dataclass
class StudentDTO:
    id: UUID
    full_name: str
    student_number: Optional[str] = None
    contact: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class StaffDTO:
    id: UUID
    full_name: str
    staff_number: Optional[str] = None
    contact: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class TeamDTO:
    id: UUID
    name: str
    modality: ModalityDTO
    course: CourseDTO
    players: List[StudentDTO]
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.modality, ModalityDTO):
            self.modality = ModalityDTO(**self.modality)

        if not isinstance(self.course, CourseDTO):
            self.course = CourseDTO(**self.course)

        self.players = [
            player if isinstance(player, StudentDTO) else StudentDTO(**player)
            for player in self.players
        ]


class ModalitiesService(BaseService):
    """Service for managing courses, modalities, teams, and students via modalities-service"""

    def __init__(self):
        base_url = os.environ.get(
            "MODALITIES_SERVICE_URL", "http://modalities-service:8000"
        )
        super().__init__(base_url)

    # ==================== NUCLEO METHODS ====================
    def list_nucleos(self) -> List[NucleoDTO]:
        """List all nucleos"""
        nucleos_data = self.get("/nucleos")
        return [NucleoDTO(**nucleo) for nucleo in nucleos_data]

    def create_nucleo(self, data: Dict[str, Any]) -> NucleoDTO:
        """Create a new nucleo"""
        nucleo_data = self.post("/nucleos", data)
        return NucleoDTO(**nucleo_data)

    def get_nucleo(self, nucleo_id: str) -> NucleoDTO:
        """Get a nucleo by ID"""
        nucleo_data = self.get(f"/nucleos/{nucleo_id}")
        return NucleoDTO(**nucleo_data)

    def update_nucleo(self, nucleo_id: str, data: Dict[str, Any]) -> NucleoDTO:
        """Update a nucleo"""
        nucleo_data = self.put(f"/nucleos/{nucleo_id}", data)
        return NucleoDTO(**nucleo_data)

    def delete_nucleo(self, nucleo_id: str) -> None:
        """Delete a nucleo"""
        self.delete(f"/nucleos/{nucleo_id}")

    # ==================== COURSE METHODS ====================
    def list_courses(self) -> List[CourseDTO]:
        """List all courses"""
        courses_data = self.get("/courses")
        return [CourseDTO(**course) for course in courses_data]

    def create_course(self, data: Dict[str, Any]) -> CourseDTO:
        """Create a new course"""
        course_data = self.post("/courses", data)
        return CourseDTO(**course_data)

    def get_course(self, course_id: str) -> CourseDTO:
        """Get a course by ID"""
        course_data = self.get(f"/courses/{course_id}")
        return CourseDTO(**course_data)

    def update_course(self, course_id: str, data: Dict[str, Any]) -> CourseDTO:
        """Update a course"""
        course_data = self.put(f"/courses/{course_id}", data)
        return CourseDTO(**course_data)

    def delete_course(self, course_id: str) -> None:
        """Delete a course"""
        self.delete(f"/courses/{course_id}")

    # ==================== MODALITY TYPE METHODS ====================
    def list_modality_types(self) -> List[ModalityTypeDTO]:
        """List all modality types"""
        modality_types_data = self.get("/modality-types")
        return [
            ModalityTypeDTO(**modality_type) for modality_type in modality_types_data
        ]

    def create_modality_type(self, data: Dict[str, Any]) -> ModalityTypeDTO:
        """Create a new modality type"""
        modality_type_data = self.post("/modality-types", data)
        return ModalityTypeDTO(**modality_type_data)

    def get_modality_type(self, modality_type_id: str) -> ModalityTypeDTO:
        """Get a modality type by ID"""
        modality_type_data = self.get(f"/modality-types/{modality_type_id}")
        return ModalityTypeDTO(**modality_type_data)

    def update_modality_type(
        self, modality_type_id: str, data: Dict[str, Any]
    ) -> ModalityTypeDTO:
        """Update a modality type"""
        modality_type_data = self.put(f"/modality-types/{modality_type_id}", data)
        return ModalityTypeDTO(**modality_type_data)

    def delete_modality_type(self, modality_type_id: str) -> None:
        """Delete a modality type"""
        self.delete(f"/modality-types/{modality_type_id}")

    # ==================== MODALITY METHODS ====================
    def list_modalities(self) -> List[ModalityDTO]:
        """List all modalities"""
        modalities_data = self.get("/modalities")
        return [ModalityDTO(**modality) for modality in modalities_data]

    def create_modality(self, name: str, modality_type_id: str) -> ModalityDTO:
        """Create a new modality"""
        data = {"name": name, "modality_type_id": modality_type_id}
        modality_data = self.post("/modalities", data)
        return ModalityDTO(**modality_data)

    def get_modality(self, modality_id: str) -> ModalityDTO:
        """Get a modality by ID"""
        modality_data = self.get(f"/modalities/{modality_id}")
        return ModalityDTO(**modality_data)

    def update_modality(self, modality_id: str, data: Dict[str, Any]) -> ModalityDTO:
        """Update a modality"""
        modality_data = self.put(f"/modalities/{modality_id}", data)
        return ModalityDTO(**modality_data)

    def delete_modality(self, modality_id: str) -> None:
        """Delete a modality"""
        self.delete(f"/modalities/{modality_id}")

    # ==================== STUDENT METHODS ====================
    def list_students(self) -> List[StudentDTO]:
        """List all students"""
        students_data = self.get("/students")
        return [StudentDTO(**student) for student in students_data]

    def create_student(self, data: Dict[str, Any]) -> StudentDTO:
        """Create a new student"""
        student_data = self.post("/students", data)
        return StudentDTO(**student_data)

    def get_student(self, student_id: str) -> StudentDTO:
        """Get a student by ID"""
        student_data = self.get(f"/students/{student_id}")
        return StudentDTO(**student_data)

    def update_student(self, student_id: str, data: Dict[str, Any]) -> StudentDTO:
        """Update a student"""
        student_data = self.put(f"/students/{student_id}", data)
        return StudentDTO(**student_data)

    def delete_student(self, student_id: str) -> None:
        """Delete a student"""
        self.delete(f"/students/{student_id}")

    def get_students_by_ids(self, student_ids: List[str]) -> List[StudentDTO]:
        """Get multiple students by their IDs"""
        students_data = self.post("/students/batch-get", student_ids)
        return [StudentDTO(**student) for student in students_data]

    # ==================== STAFF METHODS ====================
    def list_staff(self) -> List[StaffDTO]:
        """List all staff members"""
        staff_data = self.get("/staff")
        return [StaffDTO(**staff) for staff in staff_data]

    def create_staff(
        self, full_name: str, staff_number: str = None, contact: str = None
    ) -> StaffDTO:
        """Create a new staff member"""
        data = {
            "full_name": full_name,
            "staff_number": staff_number,
            "contact": contact,
        }
        staff_data = self.post("/staff", data)
        return StaffDTO(**staff_data)

    def get_staff(self, staff_id: str) -> StaffDTO:
        """Get a staff member by ID"""
        staff_data = self.get(f"/staff/{staff_id}")
        return StaffDTO(**staff_data)

    def update_staff(self, staff_id: str, data: Dict[str, Any]) -> StaffDTO:
        """Update a staff member"""
        staff_data = self.put(f"/staff/{staff_id}", data)
        return StaffDTO(**staff_data)

    def delete_staff(self, staff_id: str) -> None:
        """Delete a staff member"""
        self.delete(f"/staff/{staff_id}")

    # ==================== TEAM METHODS ====================
    def list_teams(self) -> List[TeamDTO]:
        """List all teams"""
        return self.get("/teams")

    def create_team(self, data: Dict[str, Any]) -> TeamDTO:
        """Create a new team"""
        return self.post("/teams", data)

    def get_team(self, team_id: str) -> TeamDTO:
        """Get a team by ID"""
        team_data = self.get(f"/teams/{team_id}")
        return TeamDTO(**team_data)

    def get_teams_by_ids(self, team_ids: List[str]) -> List[TeamDTO]:
        """Get multiple teams by their IDs"""
        teams_data = self.post("/teams/batch-get", team_ids)
        return [TeamDTO(**team) for team in teams_data]

    def update_team(self, team_id: str, data: Dict[str, Any]) -> TeamDTO:
        """Update a team"""
        team_data = self.put(f"/teams/{team_id}", data)
        return TeamDTO(**team_data)

    def delete_team(self, team_id: str) -> None:
        """Delete a team"""
        self.delete(f"/teams/{team_id}")


# Singleton instance
modalities_service_client = ModalitiesService()
