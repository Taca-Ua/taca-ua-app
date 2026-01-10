"""
Service for communicating with modalities-service microservice
"""

import os
from typing import Any, Dict, List

from .base_service import BaseService


class ModalitiesService(BaseService):
    """Service for managing courses, modalities, teams, and students via modalities-service"""

    def __init__(self):
        base_url = os.environ.get(
            "MODALITIES_SERVICE_URL", "http://modalities-service:8000"
        )
        super().__init__(base_url)

    # ==================== NUCLEO METHODS ====================
    def list_nucleos(self) -> List[Dict[str, Any]]:
        """List all nucleos"""
        return self.get("/nucleos")

    def create_nucleo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new nucleo"""
        return self.post("/nucleos", data)

    def get_nucleo(self, nucleo_id: str) -> Dict[str, Any]:
        """Get a nucleo by ID"""
        return self.get(f"/nucleos/{nucleo_id}")

    def update_nucleo(self, nucleo_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a nucleo"""
        return self.put(f"/nucleos/{nucleo_id}", data)

    def delete_nucleo(self, nucleo_id: str) -> None:
        """Delete a nucleo"""
        self.delete(f"/nucleos/{nucleo_id}")

    # ==================== COURSE METHODS ====================
    def list_courses(self) -> List[Dict[str, Any]]:
        """List all courses"""
        return self.get("/courses")

    def create_course(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new course"""
        return self.post("/courses", data)

    def get_course(self, course_id: str) -> Dict[str, Any]:
        """Get a course by ID"""
        return self.get(f"/courses/{course_id}")

    def update_course(self, course_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a course"""
        return self.put(f"/courses/{course_id}", data)

    def delete_course(self, course_id: str) -> None:
        """Delete a course"""
        self.delete(f"/courses/{course_id}")

    # ==================== MODALITY TYPE METHODS ====================
    def list_modality_types(self) -> List[Dict[str, Any]]:
        """List all modality types"""
        return self.get("/modality-types")

    def create_modality_type(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new modality type"""
        return self.post("/modality-types", data)

    def get_modality_type(self, modality_type_id: str) -> Dict[str, Any]:
        """Get a modality type by ID"""
        return self.get(f"/modality-types/{modality_type_id}")

    def update_modality_type(
        self, modality_type_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a modality type"""
        return self.put(f"/modality-types/{modality_type_id}", data)

    def delete_modality_type(self, modality_type_id: str) -> None:
        """Delete a modality type"""
        self.delete(f"/modality-types/{modality_type_id}")

    # ==================== MODALITY METHODS ====================
    def list_modalities(self) -> List[Dict[str, Any]]:
        """List all modalities"""
        return self.get("/modalities")

    def create_modality(self, name: str, modality_type_id: str) -> Dict[str, Any]:
        """Create a new modality"""
        data = {"name": name, "modality_type_id": modality_type_id}
        return self.post("/modalities", data)

    def get_modality(self, modality_id: str) -> Dict[str, Any]:
        """Get a modality by ID"""
        return self.get(f"/modalities/{modality_id}")

    def update_modality(self, modality_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a modality"""
        return self.put(f"/modalities/{modality_id}", data)

    def delete_modality(self, modality_id: str) -> None:
        """Delete a modality"""
        self.delete(f"/modalities/{modality_id}")

    # ==================== STUDENT METHODS ====================
    def list_students(self) -> List[Dict[str, Any]]:
        """List all students"""
        return self.get("/students")

    def create_student(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new student"""
        return self.post("/students", data)

    def get_student(self, student_id: str) -> Dict[str, Any]:
        """Get a student by ID"""
        return self.get(f"/students/{student_id}")

    def update_student(self, student_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a student"""
        return self.put(f"/students/{student_id}", data)

    def delete_student(self, student_id: str) -> None:
        """Delete a student"""
        self.delete(f"/students/{student_id}")

    # ==================== STAFF METHODS ====================
    def list_staff(self) -> List[Dict[str, Any]]:
        """List all staff members"""
        return self.get("/staff")

    def create_staff(
        self, full_name: str, staff_number: str = None, contact: str = None
    ) -> Dict[str, Any]:
        """Create a new staff member"""
        data = {
            "full_name": full_name,
            "staff_number": staff_number,
            "contact": contact,
        }
        return self.post("/staff", data)

    def get_staff(self, staff_id: str) -> Dict[str, Any]:
        """Get a staff member by ID"""
        return self.get(f"/staff/{staff_id}")

    def update_staff(self, staff_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a staff member"""
        return self.put(f"/staff/{staff_id}", data)

    def delete_staff(self, staff_id: str) -> None:
        """Delete a staff member"""
        self.delete(f"/staff/{staff_id}")

    # ==================== TEAM METHODS ====================
    def list_teams(self) -> List[Dict[str, Any]]:
        """List all teams"""
        return self.get("/teams")

    def create_team(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new team"""
        return self.post("/teams", data)

    def get_team(self, team_id: str) -> Dict[str, Any]:
        """Get a team by ID"""
        return self.get(f"/teams/{team_id}")

    def update_team(self, team_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a team"""
        return self.put(f"/teams/{team_id}", data)

    def delete_team(self, team_id: str) -> None:
        """Delete a team"""
        self.delete(f"/teams/{team_id}")


# Singleton instance
modalities_service_client = ModalitiesService()
