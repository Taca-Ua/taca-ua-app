from dataclasses import dataclass, field
from typing import List
from uuid import UUID

from admin_api.clients.keycloak_service import (
    KeycloakAdminUserDTO,
    keycloak_service_client,
)
from admin_api.clients.modalities_service import modalities_service_client


@dataclass
class _NucleoSummaryDTO:
    id: UUID
    name: str
    abbreviation: str


@dataclass
class _CourseSummaryDTO:
    id: UUID
    name: str
    abbreviation: str


@dataclass
class AdminUserDTO:
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    enabled: bool
    role: str
    nucleos: List[_NucleoSummaryDTO] = field(default_factory=list)
    courses: List[_CourseSummaryDTO] = field(default_factory=list)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __post_init__(self):
        if self.nucleos is None:
            self.nucleos = [
                (
                    nucleo_data
                    if isinstance(nucleo_data, _NucleoSummaryDTO)
                    else _NucleoSummaryDTO(**nucleo_data)
                )
                for nucleo_data in self.nucleos
            ]
        if self.courses is None:
            self.courses = [
                (
                    course_data
                    if isinstance(course_data, _CourseSummaryDTO)
                    else _CourseSummaryDTO(**course_data)
                )
                for course_data in self.courses
            ]


class AdminService:

    # Helper methods
    def _build_admin_from_keycloak_answer(
        self,
        admin_data: KeycloakAdminUserDTO,
        include_nucleos: bool = False,
        include_courses: bool = False,
    ) -> AdminUserDTO:
        """Helper method to build an AdminUserDTO from Keycloak admin data, optionally including associated nucleos."""
        admin_id = admin_data.id

        if include_nucleos:
            admin_nucleos_data = (
                modalities_service_client.nucleos.list_nucleos_by_admin(admin_id)
            )
        else:
            admin_nucleos_data = []

        if include_courses:
            admin_courses_data = (
                modalities_service_client.courses.list_courses_by_admin(admin_id)
            )
        else:
            admin_courses_data = []

        return AdminUserDTO(
            id=admin_id,
            username=admin_data.username,
            email=admin_data.email,
            first_name=admin_data.first_name,
            last_name=admin_data.last_name,
            enabled=admin_data.enabled,
            role=(
                [i for i in admin_data.roles if not i.startswith("default-roles")][0]
                if admin_data.roles
                else None
            ),
            nucleos=[
                _NucleoSummaryDTO(
                    id=nucleo.id, name=nucleo.name, abbreviation=nucleo.abbreviation
                )
                for nucleo in admin_nucleos_data
            ],
            courses=[
                _CourseSummaryDTO(
                    id=course.id, name=course.name, abbreviation=course.abbreviation
                )
                for course in admin_courses_data
            ],
        )

    # Admin user management methods
    def list_admins(self) -> List[AdminUserDTO]:
        """List all admin users in Keycloak."""
        keycloak_admins = keycloak_service_client.list_admins()

        # Build AdminUserDTOs for each admin user, including associated nucleos
        admins = []
        for admin_data in keycloak_admins:
            admins.append(self._build_admin_from_keycloak_answer(admin_data))

        return admins

    def create_admin(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str,
        nucleos_ids: List[UUID] = None,
    ) -> AdminUserDTO:
        """Create a new admin user in Keycloak and associate with nucleos if provided.

        Args:
            username (str): username of the new admin user
            email (str): email of the new admin user
            password (str): password of the new admin user
            first_name (str): first name of the new admin user
            last_name (str): last name of the new admin user
            role (str): role of the new admin user
            nucleos_ids (List[UUID], optional): list of nucleos to associate with the new admin user. Defaults to None.
        """

        if nucleos_ids is None:
            nucleos_ids = []

        # Try to create the admin user in Keycloak
        try:
            new_admin = keycloak_service_client.create_admin(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )

        except Exception as e:
            raise Exception(f"Failed to create admin user: {str(e)}")

        # If nucleos were provided, associate the new admin user with the specified nucleos
        if nucleos_ids:
            modalities_service_client.nucleos.associate_admin_with_nucleos(
                admin_id=new_admin.id,
                nucleo_ids=[str(nucleo_id) for nucleo_id in nucleos_ids],
            )

        return self._build_admin_from_keycloak_answer(new_admin)

    def get_admin(self, user_id: UUID) -> AdminUserDTO:
        """Retrieve an admin user from Keycloak by ID.

        Args:
            user_id (UUID): ID of the admin user to retrieve
        """
        try:
            keycloak_admin = keycloak_service_client.get_admin(user_id)
        except Exception as e:
            raise Exception(f"Failed to retrieve admin user: {str(e)}")

        return self._build_admin_from_keycloak_answer(
            keycloak_admin, include_nucleos=True, include_courses=True
        )

    def update_admin(
        self,
        user_id: UUID,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        enabled: bool = None,
        nucleos: List[UUID] = None,
    ) -> AdminUserDTO:
        """Update an existing admin user in Keycloak and update nucleos association if provided.

        Args:
            user_id (UUID): ID of the admin user to update
            email (str, optional): new email of the admin user. Defaults to None.
            first_name (str, optional): new first name of the admin user. Defaults to None.
            last_name (str, optional): new last name of the admin user. Defaults to None.
            enabled (bool, optional): new enabled status of the admin user. Defaults to None.
            nucleos (List[UUID], optional): list of nucleos to associate with the admin user. Defaults to None.
        """
        try:
            keycloak_admin = keycloak_service_client.update_admin(
                user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                enabled=enabled,
            )
        except Exception as e:
            raise Exception(f"Failed to update admin user: {str(e)}")

        if nucleos is not None:
            modalities_service_client.nucleos.associate_admin_with_nucleos(
                admin_id=user_id, nucleo_ids=[str(nucleo_id) for nucleo_id in nucleos]
            )

        # Retrieve the updated admin user data
        return self._build_admin_from_keycloak_answer(
            keycloak_admin, include_nucleos=True, include_courses=True
        )

    def delete_admin(self, user_id: UUID) -> None:
        """Delete an admin user from Keycloak.

        Args:
            user_id (UUID): ID of the admin user to delete
        """

        # First, disassociate the admin user from all nucleos to clean up associations in the modalities service
        try:
            modalities_service_client.nucleos.associate_admin_with_nucleos(
                admin_id=user_id, nucleo_ids=[]
            )
        except Exception as e:
            raise Exception(
                f"Failed to disassociate admin user from nucleos before deletion: {str(e)}"
            )

        # Then, delete the admin user from Keycloak
        try:
            keycloak_service_client.delete_admin(user_id)
        except Exception as e:
            raise Exception(f"Failed to delete admin user: {str(e)}")

    def change_password(
        self, user_id: UUID, new_password: str, temporary: bool = False
    ):
        """Change the password of an admin user in Keycloak.

        Args:
            user_id (UUID): ID of the admin user whose password is to be changed
            new_password (str): new password for the admin user
            temporary (bool, optional): whether the new password is temporary. Defaults to False.
        """
        try:
            keycloak_service_client.change_password(user_id, new_password, temporary)
        except Exception as e:
            raise Exception(f"Failed to change admin user password: {str(e)}")


admin_service = AdminService()
