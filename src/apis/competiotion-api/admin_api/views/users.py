"""
User management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..repositories import UserRepository
from ..serializers import (
    NucleoAdminCreateSerializer,
    NucleoAdminListSerializer,
    NucleoAdminUpdateSerializer,
)


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
        """List all nucleo administrators"""
        users = UserRepository.get_nucleo_admins()
        data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "course_id": user.course_id,
                "full_name": user.full_name,
            }
            for user in users
        ]
        return Response(data)

    def post(self, request):
        """Create a new nucleo administrator"""
        serializer = NucleoAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UserRepository.create(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                role="nucleo",
                course_id=serializer.validated_data["course_id"],
                course_abbreviation=serializer.validated_data.get("course_abbreviation"),
                full_name=serializer.validated_data.get("full_name", ""),
            )
            response_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "course_id": user.course_id,
                "full_name": user.full_name,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


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
        """Update a nucleo administrator"""
        serializer = NucleoAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UserRepository.update(
                user_id=user_id,
                full_name=serializer.validated_data.get("full_name"),
                course_id=serializer.validated_data.get("course_id"),
                course_abbreviation=serializer.validated_data.get("course_abbreviation"),
            )

            if not user:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            response_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "course_id": user.course_id,
                "full_name": user.full_name,
            }
            return Response(response_data)
        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, user_id):
        """Delete a nucleo administrator"""
        deleted = UserRepository.delete(user_id)
        if not deleted:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
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
        users = UserRepository.get_all()
        administrators = [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "course_id": user.course_id,
                "course_abbreviation": user.course_abbreviation,
            }
            for user in users
        ]
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

        # Validate role
        role = data["role"]
        if role not in ["nucleo", "geral"]:
            return Response(
                {"error": "Role must be 'nucleo' or 'geral'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserRepository.create(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=role,
                course_id=data.get("course_id"),
                course_abbreviation=data.get("course_abbreviation"),
                full_name=data["full_name"],
            )

            response_data = {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "course_id": user.course_id,
                "course_abbreviation": user.course_abbreviation,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


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
        user = UserRepository.get_by_id(admin_id)

        if not user:
            return Response(
                {"error": "Administrator not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "course_id": user.course_id,
                "course_abbreviation": user.course_abbreviation,
            },
            status=status.HTTP_200_OK,
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
        try:
            user = UserRepository.update(
                user_id=admin_id,
                username=request.data.get("username"),
                email=request.data.get("email"),
                password=request.data.get("password"),
                full_name=request.data.get("full_name"),
                course_id=request.data.get("course_id"),
                course_abbreviation=request.data.get("course_abbreviation"),
            )

            if not user:
                return Response(
                    {"error": "Administrator not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                    "course_id": user.course_id,
                    "course_abbreviation": user.course_abbreviation,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Delete administrator",
        description="Deletes an administrator from the system",
        tags=["Administrator Management"],
        responses={204: None, 404: dict},
    )
    def delete(self, request, admin_id):
        """Delete administrator"""
        deleted = UserRepository.delete(admin_id)
        if not deleted:
            return Response(
                {"error": "Administrator not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
