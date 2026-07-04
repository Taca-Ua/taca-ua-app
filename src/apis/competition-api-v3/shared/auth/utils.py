from uuid import UUID


class RolesEnum:
    GENERAL_ADMIN = "general_admin"
    NUCLEO_ADMIN = "nucleo_admin"


class User:
    def __init__(self, user_id: UUID, roles: list[str]):
        self.user_id = user_id
        self.roles = roles


def get_user(request) -> User | None:
    # Placeholder for user retrieval logic
    if not getattr(request, "user_id", None):
        return None

    u = User(user_id=UUID(request.user_id), roles=getattr(request, "roles", []))
    return u
