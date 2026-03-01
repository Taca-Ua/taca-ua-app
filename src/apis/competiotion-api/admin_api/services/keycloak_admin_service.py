"""
Keycloak Admin API service for managing admin users.
"""

import logging
from typing import Optional

from django.conf import settings
from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError

logger = logging.getLogger(__name__)


class KeycloakAdminService:
    """
    Service for interacting with Keycloak Admin API to manage admin users.
    """

    def __init__(self):
        """Initialize the Keycloak Admin client."""
        self.keycloak_admin = KeycloakAdmin(
            server_url=settings.KEYCLOAK_ADMIN_SERVER_URL,
            username=settings.KEYCLOAK_ADMIN_USERNAME,
            password=settings.KEYCLOAK_ADMIN_PASSWORD,
            realm_name=settings.KEYCLOAK_ADMIN_REALM,
            user_realm_name=settings.KEYCLOAK_ADMIN_USER_REALM,
            verify=settings.KEYCLOAK_ADMIN_VERIFY_SSL,
        )

    def create_admin(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str,
    ) -> dict:
        """
        Create a new admin user in Keycloak and assign the appropriate role.

        Args:
            username: The username for the new admin
            email: The email address of the admin
            password: The password for the admin account
            first_name: First name of the admin
            last_name: Last name of the admin
            role: The role to assign ("admin_geral" or "admin_nucleo")

        Returns:
            dict: User information including the user ID

        Raises:
            KeycloakError: If user creation fails
            ValueError: If an invalid role is provided
        """
        if role not in ["admin_geral", "admin_nucleo"]:
            raise ValueError(
                f"Invalid role: {role}. Must be 'admin_geral' or 'admin_nucleo'"
            )

        try:
            # Create the user
            user_id = self.keycloak_admin.create_user(
                {
                    "username": username,
                    "email": email,
                    "firstName": first_name,
                    "lastName": last_name,
                    "enabled": True,
                    "emailVerified": True,
                    "credentials": [
                        {
                            "type": "password",
                            "value": password,
                            "temporary": False,
                        }
                    ],
                }
            )

            logger.info(f"Created user {username} with ID {user_id}")

            # Assign the role
            self._assign_role_to_user(user_id, role)

            # Fetch and return user details
            user = self.keycloak_admin.get_user(user_id)
            return {
                "id": user_id,
                "username": user["username"],
                "email": user["email"],
                "first_name": user.get("firstName", ""),
                "last_name": user.get("lastName", ""),
                "role": role,
                "enabled": user["enabled"],
            }

        except KeycloakError as e:
            logger.error(f"Failed to create admin user {username}: {str(e)}")
            raise

    def _assign_role_to_user(self, user_id: str, role_name: str) -> None:
        """
        Assign a realm role to a user.

        Args:
            user_id: The Keycloak user ID
            role_name: The name of the role to assign

        Raises:
            KeycloakError: If role assignment fails
        """
        try:
            # Get the role object
            role = self.keycloak_admin.get_realm_role(role_name)

            # Assign the role to the user
            self.keycloak_admin.assign_realm_roles(user_id, [role])

            logger.info(f"Assigned role {role_name} to user {user_id}")

        except KeycloakError as e:
            logger.error(
                f"Failed to assign role {role_name} to user {user_id}: {str(e)}"
            )
            raise

    def get_admin(self, user_id: str) -> dict:
        """
        Retrieve an admin user by ID.

        Args:
            user_id: The Keycloak user ID

        Returns:
            dict: User information including roles

        Raises:
            KeycloakError: If user retrieval fails
        """
        try:
            user = self.keycloak_admin.get_user(user_id)
            roles = self.keycloak_admin.get_realm_roles_of_user(user_id)

            # Filter to only admin roles
            admin_roles = [
                role["name"]
                for role in roles
                if role["name"] in ["admin_geral", "admin_nucleo"]
            ]

            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "first_name": user.get("firstName", ""),
                "last_name": user.get("lastName", ""),
                "roles": admin_roles,
                "enabled": user["enabled"],
            }

        except KeycloakError as e:
            logger.error(f"Failed to retrieve user {user_id}: {str(e)}")
            raise

    def list_admins(self) -> list[dict]:
        """
        List all admin users (users with admin_geral or admin_nucleo roles).

        Returns:
            list[dict]: List of admin users with their information

        Raises:
            KeycloakError: If listing fails
        """
        try:
            all_admins = []

            # Get users with each admin role
            for role_name in ["admin_geral", "admin_nucleo"]:
                try:
                    users = self.keycloak_admin.get_realm_role_members(role_name)
                    for user in users:
                        # Check if we've already added this user
                        if not any(admin["id"] == user["id"] for admin in all_admins):
                            roles = self.keycloak_admin.get_realm_roles_of_user(
                                user["id"]
                            )
                            admin_roles = [
                                role["name"]
                                for role in roles
                                if role["name"] in ["admin_geral", "admin_nucleo"]
                            ]

                            all_admins.append(
                                {
                                    "id": user["id"],
                                    "username": user["username"],
                                    "email": user.get("email", ""),
                                    "first_name": user.get("firstName", ""),
                                    "last_name": user.get("lastName", ""),
                                    "roles": admin_roles,
                                    "enabled": user["enabled"],
                                }
                            )
                except KeycloakError as e:
                    logger.warning(
                        f"Failed to get users for role {role_name}: {str(e)}"
                    )

            return all_admins

        except KeycloakError as e:
            logger.error(f"Failed to list admin users: {str(e)}")
            raise

    def update_admin(
        self,
        user_id: str,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> dict:
        """
        Update an admin user's information.

        Args:
            user_id: The Keycloak user ID
            email: New email address (optional)
            first_name: New first name (optional)
            last_name: New last name (optional)
            enabled: Enable/disable the account (optional)

        Returns:
            dict: Updated user information

        Raises:
            KeycloakError: If update fails
        """
        try:
            update_payload = {}

            if email is not None:
                update_payload["email"] = email
            if first_name is not None:
                update_payload["firstName"] = first_name
            if last_name is not None:
                update_payload["lastName"] = last_name
            if enabled is not None:
                update_payload["enabled"] = enabled

            if update_payload:
                self.keycloak_admin.update_user(user_id, update_payload)
                logger.info(f"Updated user {user_id}")

            return self.get_admin(user_id)

        except KeycloakError as e:
            logger.error(f"Failed to update user {user_id}: {str(e)}")
            raise

    def delete_admin(self, user_id: str) -> None:
        """
        Delete an admin user from Keycloak.

        Args:
            user_id: The Keycloak user ID

        Raises:
            KeycloakError: If deletion fails
        """
        try:
            self.keycloak_admin.delete_user(user_id)
            logger.info(f"Deleted user {user_id}")

        except KeycloakError as e:
            logger.error(f"Failed to delete user {user_id}: {str(e)}")
            raise

    def change_password(
        self, user_id: str, new_password: str, temporary: bool = False
    ) -> None:
        """
        Change an admin user's password.

        Args:
            user_id: The Keycloak user ID
            new_password: The new password
            temporary: Whether the password is temporary (user must change on next login)

        Raises:
            KeycloakError: If password change fails
        """
        try:
            self.keycloak_admin.set_user_password(user_id, new_password, temporary)
            logger.info(f"Changed password for user {user_id}")

        except KeycloakError as e:
            logger.error(f"Failed to change password for user {user_id}: {str(e)}")
            raise


# Singleton instance
keycloak_admin_service = KeycloakAdminService()
