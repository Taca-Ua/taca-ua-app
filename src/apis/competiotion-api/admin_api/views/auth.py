"""
Authentication views — Keycloak-only.

The legacy mock session system has been removed.  Authentication is now
handled entirely by Keycloak (PKCE flow in the frontend) and validated
server-side by ``KeycloakJWTMiddleware``, which populates:

    request.user_id   — Keycloak ``sub`` (UUID string)
    request.roles     — realm-level role list from ``realm_access.roles``
"""

from django.urls.conf import path
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..decorators import require_auth
from ..serializers.auth import UserInfoSerializer


@extend_schema(
    responses={
        200: UserInfoSerializer,
        401: None,
    },
    description=(
        "Return identity information for the currently authenticated user. "
        "Requires a valid Keycloak Bearer token."
    ),
    tags=["Authentication"],
)
@api_view(["GET"])
@require_auth
def me(request):
    """
    Return the caller's Keycloak subject and realm roles as extracted by
    ``KeycloakJWTMiddleware``.
    """
    return Response(
        {
            "user_id": request.user_id,
            "roles": request.roles,
            "username": getattr(request, "username", None),
        },
        status=status.HTTP_200_OK,
    )


urlpatterns = [
    path("me/", me, name="admin_me"),
]
