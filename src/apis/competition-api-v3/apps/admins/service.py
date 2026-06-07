from typing import Optional
from uuid import UUID

from django.db import transaction
from shared.auth.keycloak_service import keycloak_service_client

from .models import Admin


@transaction.atomic
def create_admin(
    username: str,
    email: str,
    password: str,
    name: str,
    role: str,
    nucleos: list[UUID] | None = None,
):
    """Create a new admin user in Keycloak and the local database."""

    name = name.title()  # Ensure the name is properly capitalized

    # Create user in Keycloak
    keycloak_user = keycloak_service_client.create_admin(
        username=username,
        email=email,
        password=password,
        first_name=name.split()[0] if name else None,
        last_name=" ".join(name.split()[1:]) if name else None,
        role=role,
    )

    # Create corresponding Admin record in the local database
    admin = Admin.objects.create(
        id=keycloak_user.id, username=username, name=name, email=email, role=role
    )

    if nucleos:
        admin.nucleos.set(nucleos)

    return admin


@transaction.atomic
def update_admin(
    user_id: UUID,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    enabled: Optional[bool] = None,
    nucleos: Optional[list[UUID]] = None,
):
    """Update an existing admin user's information in Keycloak and the local database."""
    # Update user in Keycloak
    keycloak_service_client.update_admin(
        user_id=str(user_id),
        email=email,
        first_name=first_name,
        last_name=last_name,
        enabled=enabled,
    )

    # Update corresponding Admin record in the local database
    admin = Admin.objects.get(id=user_id)
    if email is not None:
        admin.email = email

    if first_name is not None and last_name is not None:
        admin.name = f"{first_name} {last_name}".title()
    elif (first_name, last_name) != (None, None):
        raise ValueError(
            "Both first_name and last_name must be provided together for name update."
        )

    if nucleos is not None:
        admin.nucleos.set(nucleos)

    return admin


@transaction.atomic
def delete_admin(): ...


@transaction.atomic
def change_admin_password(): ...
