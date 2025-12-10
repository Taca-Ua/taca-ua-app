"""
Service for communicating with modalities-service microservice
"""

import os
from typing import Any, Dict, List, Optional

from .base_service import BaseService


class ModalitiesService(BaseService):
    """Service for managing courses, modalities, teams, and students via modalities-service"""

    def __init__(self):
        base_url = os.environ.get(
            "MODALITIES_SERVICE_URL", "http://modalities-service:8000"
        )
        super().__init__(base_url)

    # ==================== Course Management ====================

    def create_course(
        self,
        name: str,
        abbreviation: str,
        created_by: str,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new course

        Args:
            name: Course name
            abbreviation: Course abbreviation (must be unique)
            created_by: UUID of the user creating
            description: Optional course description
            logo_url: Optional course logo URL

        Returns:
            Created course data
        """
        data = {
            "name": name,
            "abbreviation": abbreviation,
            "created_by": created_by,
        }

        if description is not None:
            data["description"] = description
        if logo_url is not None:
            data["logo_url"] = logo_url

        return self.post("/courses", data)

    def list_courses(
        self, search: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """
        List courses with optional search

        Args:
            search: Optional search term for name or abbreviation
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Dictionary with courses list, total, limit, offset
        """
        params = {"limit": limit, "offset": offset}

        if search:
            params["search"] = search

        return self.get("/courses", params=params)

    def get_course(self, course_id: str) -> Dict[str, Any]:
        """
        Get course details

        Args:
            course_id: UUID of the course

        Returns:
            Course data
        """
        return self.get(f"/courses/{course_id}")

    def update_course(
        self,
        course_id: str,
        updated_by: str,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a course

        Args:
            course_id: UUID of the course
            updated_by: UUID of the user updating
            name: Optional new name
            abbreviation: Optional new abbreviation
            description: Optional new description
            logo_url: Optional new logo URL

        Returns:
            Updated course data
        """
        data = {"updated_by": updated_by}

        if name is not None:
            data["name"] = name
        if abbreviation is not None:
            data["abbreviation"] = abbreviation
        if description is not None:
            data["description"] = description
        if logo_url is not None:
            data["logo_url"] = logo_url

        return self.put(f"/courses/{course_id}", data)

    def delete_course(self, course_id: str) -> Dict[str, Any]:
        """
        Delete a course (and all associated teams and students)

        Args:
            course_id: UUID of the course

        Returns:
            Empty dict on success
        """
        return self.delete(f"/courses/{course_id}")

    # ==================== Modality Type Management ====================
    def list_modality_types(self) -> List[Dict[str, Any]]:
        """
        List all modality types

        Returns:
            List of modality types
        """
        return self.get("/modality-types")

    def create_modality_type(
        self,
        name: str,
        description: Optional[str],
        escaloes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create a new modality type

        Args:
            name: Modality type name
            description: Optional description
            escaloes: List of escaloes

        Returns:
            Created modality type data
        """
        data = {
            "name": name,
            "description": description,
            "escaloes": escaloes,
        }

        return self.post("/modality-types", data)

    def get_modality_type(self, modality_id: str) -> Dict[str, Any]:
        """
        Get modality type details

        Args:
            modality_id: UUID of the modality type

        Returns:
            Modality type data
        """
        return self.get(f"/modality-types/{modality_id}")

    def update_modality_type(
        self,
        modality_type_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        escaloes: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update a modality type

        Args:
            modality_type_id: UUID of the modality type
            name: Optional new name
            description: Optional new description
            escaloes: Optional new escaloes list

        Returns:
            Updated modality type data
        """
        data = {}

        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if escaloes is not None:
            data["escaloes"] = escaloes

        return self.put(f"/modality-types/{modality_type_id}", data)

    def delete_modality_type(self, modality_type_id: str) -> Dict[str, Any]:
        """
        Delete a modality type

        Args:
            modality_type_id: UUID of the modality type

        Returns:
            Empty dict on success
        """
        return self.delete(f"/modality-types/{modality_type_id}")

    # ==================== Modality Management ====================

    def create_modality(
        self,
        name: str,
        type: str,
        created_by: str,
        scoring_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new modality

        Args:
            name: Modality name
            type: Type (coletiva, individual, mista)
            created_by: UUID of the user creating
            scoring_schema: Optional scoring schema (JSON)

        Returns:
            Created modality data
        """
        data = {"name": name, "type": type, "created_by": created_by}

        if scoring_schema is not None:
            data["scoring_schema"] = scoring_schema

        return self.post("/modalities", data)

    def list_modalities(
        self, type: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List modalities with optional filters

        Args:
            type: Filter by type
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of modalities
        """
        params = {"limit": limit, "offset": offset}

        if type:
            params["type"] = type

        return self.get("/modalities", params=params)

    def get_modality(self, modality_id: str) -> Dict[str, Any]:
        """
        Get modality details

        Args:
            modality_id: UUID of the modality

        Returns:
            Modality data
        """
        return self.get(f"/modalities/{modality_id}")

    def update_modality(
        self,
        modality_id: str,
        updated_by: str,
        name: Optional[str] = None,
        type: Optional[str] = None,
        scoring_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a modality

        Args:
            modality_id: UUID of the modality
            updated_by: UUID of the user updating
            name: Optional new name
            type: Optional new type
            scoring_schema: Optional new scoring schema

        Returns:
            Updated modality data
        """
        data = {"updated_by": updated_by}

        if name is not None:
            data["name"] = name
        if type is not None:
            data["type"] = type
        if scoring_schema is not None:
            data["scoring_schema"] = scoring_schema

        return self.put(f"/modalities/{modality_id}", data)

    def delete_modality(self, modality_id: str) -> Dict[str, Any]:
        """
        Delete a modality

        Args:
            modality_id: UUID of the modality

        Returns:
            Empty dict on success
        """
        return self.delete(f"/modalities/{modality_id}")

    # ==================== Team Management ====================

    def create_team(
        self,
        modality_id: str,
        course_id: str,
        created_by: str,
        name: Optional[str] = None,
        players: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new team

        Args:
            modality_id: UUID of the modality
            course_id: UUID of the course
            created_by: UUID of the user creating
            name: Optional team name (auto-generated if not provided)
            players: Optional list of student UUIDs

        Returns:
            Created team data
        """
        data = {
            "modality_id": modality_id,
            "course_id": course_id,
            "created_by": created_by,
        }

        if name is not None:
            data["name"] = name
        if players is not None:
            data["players"] = players

        return self.post("/teams", data)

    def list_teams(
        self,
        modality_id: Optional[str] = None,
        course_id: Optional[str] = None,
        tournament_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List teams with optional filters

        Args:
            modality_id: Filter by modality
            course_id: Filter by course
            tournament_id: Filter by tournament
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of teams
        """
        params = {"limit": limit, "offset": offset}

        if modality_id:
            params["modality_id"] = modality_id
        if course_id:
            params["course_id"] = course_id
        if tournament_id:
            params["tournament_id"] = tournament_id

        return self.get("/teams", params=params)

    def get_team(self, team_id: str) -> Dict[str, Any]:
        """
        Get team details

        Args:
            team_id: UUID of the team

        Returns:
            Team data
        """
        return self.get(f"/teams/{team_id}")

    def update_team(
        self,
        team_id: str,
        updated_by: str,
        name: Optional[str] = None,
        players_add: Optional[List[str]] = None,
        players_remove: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Update a team

        Args:
            team_id: UUID of the team
            updated_by: UUID of the user updating
            name: Optional new name
            players_add: Optional list of player UUIDs to add
            players_remove: Optional list of player UUIDs to remove

        Returns:
            Updated team data
        """
        data = {"updated_by": updated_by}

        if name is not None:
            data["name"] = name
        if players_add is not None:
            data["players_add"] = players_add
        if players_remove is not None:
            data["players_remove"] = players_remove

        return self.put(f"/teams/{team_id}", data)

    def delete_team(self, team_id: str) -> Dict[str, Any]:
        """
        Delete a team

        Args:
            team_id: UUID of the team

        Returns:
            Empty dict on success
        """
        return self.delete(f"/teams/{team_id}")

    # ==================== Student Management ====================

    def create_student(
        self,
        course_id: str,
        full_name: str,
        student_number: str,
        created_by: str,
        email: Optional[str] = None,
        is_member: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new student

        Args:
            course_id: UUID of the course
            full_name: Student's full name
            student_number: Unique student number
            created_by: UUID of the user creating
            email: Optional email
            is_member: Whether student is a member

        Returns:
            Created student data
        """
        data = {
            "course_id": course_id,
            "full_name": full_name,
            "student_number": student_number,
            "created_by": created_by,
            "is_member": is_member,
        }

        if email is not None:
            data["email"] = email

        return self.post("/students", data)

    def list_students(
        self,
        course_id: str,
        is_member: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List students with optional filters

        Args:
            course_id: Course UUID (required in practice)
            is_member: Filter by member status
            search: Search by name or student number
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of students
        """
        params = {"course_id": course_id, "limit": limit, "offset": offset}

        if is_member is not None:
            params["is_member"] = is_member
        if search:
            params["search"] = search

        return self.get("/students", params=params)

    def get_student(self, student_id: str) -> Dict[str, Any]:
        """
        Get student details

        Args:
            student_id: UUID of the student

        Returns:
            Student data
        """
        return self.get(f"/students/{student_id}")

    def update_student(
        self,
        student_id: str,
        updated_by: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        is_member: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update a student

        Args:
            student_id: UUID of the student
            updated_by: UUID of the user updating
            full_name: Optional new full name
            email: Optional new email
            is_member: Optional new member status

        Returns:
            Updated student data
        """
        data = {"updated_by": updated_by}

        if full_name is not None:
            data["full_name"] = full_name
        if email is not None:
            data["email"] = email
        if is_member is not None:
            data["is_member"] = is_member

        return self.put(f"/students/{student_id}", data)
