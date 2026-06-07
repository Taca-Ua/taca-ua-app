"""
Keycloak Admin API service for managing admin users.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from django.conf import settings
from keycloak import KeycloakAdmin, KeycloakError

logger = logging.getLogger(__name__)


@dataclass
class KeycloakAdminUserDTO:
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    roles: Optional[List[str]]
    enabled: bool


class KeycloakService:
    """
    Service for interacting with Keycloak API.
    """

    def __init__(self):
        """Initialize the Keycloak client."""
        # python-keycloak >= 3.x requires server_url to end with a slash.
        server_url = settings.KEYCLOAK_ADMIN_SERVER_URL.rstrip("/") + "/"
        self.keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=settings.KEYCLOAK_ADMIN_USERNAME,
            password=settings.KEYCLOAK_ADMIN_PASSWORD,
            realm_name=settings.KEYCLOAK_ADMIN_REALM,
            user_realm_name=settings.KEYCLOAK_ADMIN_USER_REALM,
            verify=settings.KEYCLOAK_ADMIN_VERIFY_SSL,
        )

        # Verify connection to Keycloak server
        try:
            self.keycloak_admin.get_server_info()
            logger.info("Successfully connected to Keycloak server")
        except KeycloakError as e:
            logger.error(f"Failed to connect to Keycloak server: {str(e)}")
            raise Exception(f"Failed to connect to Keycloak server: {str(e)}")

    def _assign_role_to_user(self, user_id: str, role_name: str) -> None:
        """
        Assign a realm role to a user.

        Args:
            user_id: The Keycloak user ID
            role_name: The name of the role to assign

        Raises:
            KeycloakError: If role assignment fails
        """
        # Get the role object
        role = self.keycloak_admin.get_realm_role(role_name)

        # Assign the role to the user
        self.keycloak_admin.assign_realm_roles(user_id, [role])

        logger.info(f"Assigned role {role_name} to user {user_id}")

    def list_admins(self) -> List[KeycloakAdminUserDTO]:
        """List all admin users in Keycloak."""
        roles = self.keycloak_admin.get_realm_roles()

        admin_roles = {}
        for role in roles:
            admins = self.keycloak_admin.get_realm_role_members(role["name"])
            for admin in admins:
                admin_id = admin["id"]
                if admin_id not in admin_roles:
                    admin_roles[admin_id] = []
                admin_roles[admin_id].append(role["name"])

        return [
            KeycloakAdminUserDTO(
                id=admin["id"],
                username=admin["username"],
                email=admin["email"],
                first_name=admin["firstName"],
                last_name=admin.get("lastName", ""),
                roles=admin_roles.get(admin["id"], []),
                enabled=admin["enabled"],
            )
            for admin in self.keycloak_admin.get_users()
        ]

    def get_admin(self, user_id: str) -> KeycloakAdminUserDTO:
        """Retrieve an admin user from Keycloak by ID."""
        admin_data = self.keycloak_admin.get_user(user_id)
        return KeycloakAdminUserDTO(
            id=admin_data["id"],
            username=admin_data["username"],
            email=admin_data["email"],
            first_name=admin_data["firstName"],
            last_name=admin_data.get("lastName", ""),
            roles=[
                role.get("name")
                for role in self.keycloak_admin.get_realm_roles_of_user(user_id)
            ],
            enabled=admin_data["enabled"],
        )

    def get_multiple_admins(
        self, user_ids: Set[str]
    ) -> Dict[str, KeycloakAdminUserDTO]:
        """Retrieve multiple admin users from Keycloak by their IDs."""
        admins = {}
        for user in self.keycloak_admin.get_users():
            if user["id"] in user_ids:
                admins[user["id"]] = KeycloakAdminUserDTO(
                    id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    first_name=user["firstName"],
                    last_name=user.get("lastName", ""),
                    roles=[
                        role.get("name")
                        for role in self.keycloak_admin.get_realm_roles_of_user(
                            user["id"]
                        )
                    ],
                    enabled=user["enabled"],
                )

        return admins

    def create_admin(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str,
    ) -> KeycloakAdminUserDTO:
        """Create a new admin user in Keycloak"""
        user_id = self.keycloak_admin.create_user(
            payload={
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{"value": password, "type": "password"}],
            }
        )

        try:
            self._assign_role_to_user(user_id, role)
        except KeycloakError as e:
            logger.error(f"Failed to assign role {role} to user {user_id}: {str(e)}")
            self.delete_admin(
                user_id
            )  # Rollback user creation if role assignment fails
            raise Exception(f"Failed to create admin user: {str(e)}")

        return self.get_admin(user_id)

    def update_admin(
        self,
        user_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> KeycloakAdminUserDTO:
        """Update an existing admin user in Keycloak."""

        # Build the update payload with only the fields that are provided
        payload = {}
        if email is not None:
            payload["email"] = email
        if first_name is not None:
            payload["firstName"] = first_name
        if last_name is not None:
            payload["lastName"] = last_name
        if enabled is not None:
            payload["enabled"] = enabled

        self.keycloak_admin.update_user(user_id, payload=payload)

        return self.get_admin(user_id)

    def delete_admin(self, user_id: str) -> None:
        """Delete an admin user from Keycloak by ID."""
        self.keycloak_admin.delete_user(user_id)

    def change_password(
        self, user_id: str, new_password: str, temporary: bool = False
    ) -> None:
        """Change the password of an admin user in Keycloak.

        Args:
            user_id (str): ID of the admin user to change password for
            new_password (str): new password to set for the admin user
            temporary (bool, optional): whether the new password should be temporary. Defaults to False.
        """
        self.keycloak_admin.set_user_password(
            user_id=user_id, password=new_password, temporary=temporary
        )


keycloak_service_client = KeycloakService()
