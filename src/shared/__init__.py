"""Shared utilities and modules for Taca-UA services."""

from .auth import (
    get_user_email,
    get_user_id,
    get_user_roles,
    get_username,
    require_role,
    verify_token,
    verify_token_optional,
)

__all__ = [
    "verify_token",
    "verify_token_optional",
    "require_role",
    "get_user_id",
    "get_user_roles",
    "get_user_email",
    "get_username",
]
