"""
User management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    NucleoAdminCreateSerializer,
    NucleoAdminListSerializer,
    NucleoAdminUpdateSerializer,
)
from .auth import MOCK_USERS


@extend_schema_view(
    get=extend_schema(
        responses=NucleoAdminListSerializer(many=True),
        description="List nucleo administrators",
        tags=["User Management"],
    ),
    post=extend_schema(
        request=NucleoAdminCreateSerializer,
        responses=NucleoAdminListSerializer,
        description="Create nucleo administrator",
        tags=["User Management"],
    ),
)
class NucleoAdminListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "username": "admin_mect",
                "email": "admin@mect.ua.pt",
                "course_id": 1,
                "full_name": "João Silva",
            },
            {
                "id": 2,
                "username": "admin_lei",
                "email": "admin@lei.ua.pt",
                "course_id": 2,
                "full_name": "Maria Santos",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = NucleoAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 3, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=NucleoAdminUpdateSerializer,
        responses=NucleoAdminListSerializer,
        description="Update nucleo administrator",
        tags=["User Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete nucleo administrator",
        tags=["User Management"],
    ),
)
class NucleoAdminDetailView(APIView):
    def put(self, request, user_id):
        serializer = NucleoAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": user_id,
            "username": f"admin_user_{user_id}",
            "email": f"admin{user_id}@example.pt",
            **serializer.validated_data,
        }
        return Response(dummy_response)

    def delete(self, request, user_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


# Administrator Management (both nucleo and geral)
class AdministratorListCreateView(APIView):
    """
    GET: List all administrators (both nucleo and geral)
    POST: Create a new administrator
    """

    @extend_schema(
        summary="List all administrators",
        description="Returns a list of all administrators in the system",
        tags=["Administrator Management"],
        responses={200: dict},
    )
    def get(self, request):
        """Return all administrators"""
        administrators = []
        for username, user_data in MOCK_USERS.items():
            admin = {
                "id": user_data["id"],
                "username": user_data["username"],
                "full_name": user_data["full_name"],
                "email": user_data["email"],
                "role": user_data["role"],
                "course_id": user_data["course_id"],
                "course_abbreviation": user_data["course_abbreviation"],
            }
            administrators.append(admin)

        return Response(administrators, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new administrator",
        description="Creates a new administrator (nucleo or geral)",
        tags=["Administrator Management"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "full_name": {"type": "string"},
                    "email": {"type": "string"},
                    "role": {"type": "string", "enum": ["nucleo", "geral"]},
                    "course_id": {"type": "integer", "nullable": True},
                },
                "required": ["username", "password", "full_name", "email", "role"],
            }
        },
        responses={201: dict, 400: dict},
    )
    def post(self, request):
        """Create a new administrator"""
        data = request.data

        # Validation
        required_fields = ["username", "password", "full_name", "email", "role"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"Field '{field}' is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        username = data["username"]

        # Check if username already exists
        if username in MOCK_USERS:
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate role
        role = data["role"]
        if role not in ["nucleo", "geral"]:
            return Response(
                {"error": "Role must be 'nucleo' or 'geral'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # For nucleo admins, course_id is required
        if role == "nucleo" and not data.get("course_id"):
            return Response(
                {"error": "course_id is required for nucleo administrators"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate new ID
        max_id = max(user["id"] for user in MOCK_USERS.values())
        new_id = max_id + 1

        # Get course abbreviation if course_id provided
        course_abbreviation = None
        if data.get("course_id"):
            # Mock course abbreviations mapping
            course_abbr_map = {
                1: "MECT",
                2: "LEI",
                3: "LECI",
                4: "BIOMED",
                5: "MMAT",
            }
            course_abbreviation = course_abbr_map.get(data["course_id"])

        # Create new administrator
        new_admin = {
            "id": new_id,
            "username": username,
            "password": data["password"],  # In production, this would be hashed
            "full_name": data["full_name"],
            "email": data["email"],
            "role": role,
            "course_id": data.get("course_id"),
            "course_abbreviation": course_abbreviation,
        }

        # Add to MOCK_USERS
        MOCK_USERS[username] = new_admin

        # Return without password
        response_data = {
            "id": new_admin["id"],
            "username": new_admin["username"],
            "full_name": new_admin["full_name"],
            "email": new_admin["email"],
            "role": new_admin["role"],
            "course_id": new_admin["course_id"],
            "course_abbreviation": new_admin["course_abbreviation"],
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class AdministratorDetailView(APIView):
    """
    GET: Retrieve a specific administrator
    PUT: Update an administrator
    DELETE: Delete an administrator
    """

    @extend_schema(
        summary="Get administrator details",
        description="Returns details of a specific administrator",
        tags=["Administrator Management"],
        responses={200: dict, 404: dict},
    )
    def get(self, request, admin_id):
        """Get administrator by ID"""
        for user_data in MOCK_USERS.values():
            if user_data["id"] == admin_id:
                return Response(
                    {
                        "id": user_data["id"],
                        "username": user_data["username"],
                        "full_name": user_data["full_name"],
                        "email": user_data["email"],
                        "role": user_data["role"],
                        "course_id": user_data["course_id"],
                        "course_abbreviation": user_data["course_abbreviation"],
                        "password": user_data[
                            "password"
                        ],  # Include password for admin view
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"error": "Administrator not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        summary="Update administrator",
        description="Updates an existing administrator",
        tags=["Administrator Management"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "full_name": {"type": "string"},
                    "email": {"type": "string"},
                    "course_id": {"type": "integer", "nullable": True},
                },
            }
        },
        responses={200: dict, 404: dict, 400: dict},
    )
    def put(self, request, admin_id):
        """Update administrator"""
        # Find the administrator
        target_username = None
        for username, user_data in MOCK_USERS.items():
            if user_data["id"] == admin_id:
                target_username = username
                break

        if not target_username:
            return Response(
                {"error": "Administrator not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_data = MOCK_USERS[target_username]

        # Update fields if provided
        if "username" in request.data and request.data["username"] != target_username:
            new_username = request.data["username"]
            # Check if new username already exists
            if new_username in MOCK_USERS:
                return Response(
                    {"error": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Move to new username key
            MOCK_USERS[new_username] = MOCK_USERS.pop(target_username)
            MOCK_USERS[new_username]["username"] = new_username
            target_username = new_username

        if "password" in request.data and request.data["password"]:
            MOCK_USERS[target_username]["password"] = request.data["password"]

        if "full_name" in request.data:
            MOCK_USERS[target_username]["full_name"] = request.data["full_name"]

        if "email" in request.data:
            MOCK_USERS[target_username]["email"] = request.data["email"]

        if "course_id" in request.data:
            course_id = request.data["course_id"]
            MOCK_USERS[target_username]["course_id"] = course_id

            # Update course abbreviation
            if course_id:
                course_abbr_map = {
                    1: "MECT",
                    2: "LEI",
                    3: "LECI",
                    4: "BIOMED",
                    5: "MMAT",
                }
                MOCK_USERS[target_username]["course_abbreviation"] = (
                    course_abbr_map.get(course_id)
                )
            else:
                MOCK_USERS[target_username]["course_abbreviation"] = None

        # Return updated data without password
        updated_data = MOCK_USERS[target_username]
        return Response(
            {
                "id": updated_data["id"],
                "username": updated_data["username"],
                "full_name": updated_data["full_name"],
                "email": updated_data["email"],
                "role": updated_data["role"],
                "course_id": updated_data["course_id"],
                "course_abbreviation": updated_data["course_abbreviation"],
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete administrator",
        description="Deletes an administrator from the system",
        tags=["Administrator Management"],
        responses={204: None, 404: dict},
    )
    def delete(self, request, admin_id):
        """Delete administrator"""
        # Find and delete the administrator
        for username, user_data in list(MOCK_USERS.items()):
            if user_data["id"] == admin_id:
                del MOCK_USERS[username]
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"error": "Administrator not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
