"""
Authentication views for admin API
Simple mock authentication for nucleo admins
TO BE REPLACED WITH PROPER AUTHENTICATION IN PRODUCTION
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    UserInfoSerializer,
)

# Mock database of nucleo admins and geral admins
MOCK_USERS = {
    # Nucleo admins (course-specific)
    "admin_mect": {
        "id": 1,
        "username": "admin_mect",
        "password": "password123",  # In production, this would be hashed
        "email": "admin@mect.ua.pt",
        "course_id": 1,
        "course_abbreviation": "MECT",
        "full_name": "João Silva",
        "role": "nucleo",
    },
    "admin_lei": {
        "id": 2,
        "username": "admin_lei",
        "password": "password123",
        "email": "admin@lei.ua.pt",
        "course_id": 2,
        "course_abbreviation": "LEI",
        "full_name": "Maria Santos",
        "role": "nucleo",
    },
    "admin_leci": {
        "id": 3,
        "username": "admin_leci",
        "password": "password123",
        "email": "admin@leci.ua.pt",
        "course_id": 3,
        "course_abbreviation": "LECI",
        "full_name": "Pedro Oliveira",
        "role": "nucleo",
    },
    "admin_biomed": {
        "id": 4,
        "username": "admin_biomed",
        "password": "password123",
        "email": "admin@biomed.ua.pt",
        "course_id": 4,
        "course_abbreviation": "BIOMED",
        "full_name": "Ana Costa",
        "role": "nucleo",
    },
    "admin_mmat": {
        "id": 5,
        "username": "admin_mmat",
        "password": "password123",
        "email": "admin@mmat.ua.pt",
        "course_id": 5,
        "course_abbreviation": "MMAT",
        "full_name": "Carlos Ferreira",
        "role": "nucleo",
    },
    # Geral admins (global access)
    "admin_geral": {
        "id": 100,
        "username": "admin_geral",
        "password": "password123",
        "email": "geral@taca.ua.pt",
        "course_id": None,
        "course_abbreviation": None,
        "full_name": "Administrador Geral",
        "role": "geral",
    },
    "admin_taca": {
        "id": 101,
        "username": "admin_taca",
        "password": "password123",
        "email": "admin@taca.ua.pt",
        "course_id": None,
        "course_abbreviation": None,
        "full_name": "Admin TACA",
        "role": "geral",
    },
}

# Mock sessions storage (in production, use proper session management)
MOCK_SESSIONS = {}


@extend_schema(
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        401: None,
    },
    description="Login for nucleo administrators. Returns session token and user info.",
    tags=["Authentication"],
)
@api_view(["POST"])
def login(request):
    """
    Simple login endpoint for nucleo administrators.
    Returns a session token and user information.
    """
    serializer = LoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    # Check credentials
    user = MOCK_USERS.get(username)
    if not user or user["password"] != password:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Create session token (simple mock)
    session_token = f"session_{user['id']}_{username}"
    MOCK_SESSIONS[session_token] = user

    # Return response without password
    user_data = {k: v for k, v in user.items() if k != "password"}
    response_data = {
        "token": session_token,
        "user": user_data,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    responses={
        200: UserInfoSerializer,
        401: None,
    },
    description="Get current authenticated user information",
    tags=["Authentication"],
)
@api_view(["GET"])
def me(request):
    """
    Get current authenticated user information.
    Requires Authorization header with Bearer token.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response(
            {"error": "Missing or invalid authorization header"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = auth_header.replace("Bearer ", "")
    user = MOCK_SESSIONS.get(token)

    if not user:
        return Response(
            {"error": "Invalid or expired token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Return user data without password
    user_data = {k: v for k, v in user.items() if k != "password"}
    return Response(user_data, status=status.HTTP_200_OK)


@extend_schema(
    responses={204: None},
    description="Logout current user and invalidate session token",
    tags=["Authentication"],
)
@api_view(["POST"])
def logout(request):
    """
    Logout current user and invalidate session token.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        if token in MOCK_SESSIONS:
            del MOCK_SESSIONS[token]

    return Response(status=status.HTTP_204_NO_CONTENT)


def get_authenticated_user(request):
    """
    Helper function to get authenticated user from request.
    Returns user dict or None if not authenticated.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")
    return MOCK_SESSIONS.get(token)
