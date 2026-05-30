from uuid import UUID


class User:
    def __init__(self, user_id: UUID, roles: list[str]):
        self.user_id = user_id
        self.roles = roles


def get_user(request) -> User | None:
    # Placeholder for user retrieval logic
    return User(
        user_id=UUID("12345678-1234-5678-1234-567812345678"), roles=["general_admin"]
    )
