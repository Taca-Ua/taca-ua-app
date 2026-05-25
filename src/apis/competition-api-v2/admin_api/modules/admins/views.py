from admin_api.utils.decorators import RoleRequiredMixin, require_roles_class_method
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from keycloak.exceptions import KeycloakError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AdminCreateSerializer,
    AdminDetailSerializer,
    AdminListSerializer,
    AdminPasswordChangeSerializer,
    AdminUpdateSerializer,
)
from .service import admin_service


@extend_schema_view(
    get=extend_schema(
        responses=AdminListSerializer(many=True),
        description="List all admin users with 'general_admin' or 'admin_nucleo' roles",
        tags=["Admin Management"],
    ),
    post=extend_schema(
        request=AdminCreateSerializer,
        responses={201: AdminListSerializer},
        description="Create a new admin user in Keycloak with the specified role",
        tags=["Admin Management"],
    ),
)
class AdminListCreateView(RoleRequiredMixin, APIView):
    """
    View for listing and creating admin users.
    Requires 'general_admin' role.
    """

    def get(self, request):
        """List all admin users."""
        try:
            admins = admin_service.list_admins()
            serializer = AdminListSerializer(admins, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeycloakError as e:
            return Response(
                {"error": "Failed to retrieve admins", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @require_roles_class_method("general_admin")
    def post(self, request):
        """Create a new admin user."""
        serializer = AdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            admin = admin_service.create_admin(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                role=serializer.validated_data["role"],
                nucleos_ids=serializer.validated_data.get("nucleos", []),
            )

            response_serializer = AdminListSerializer(admin)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeycloakError as e:
            return Response(
                {"error": "Failed to create admin", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema_view(
    get=extend_schema(
        responses=AdminDetailSerializer,
        description="Retrieve details of a specific admin user",
        tags=["Admin Management"],
    ),
    put=extend_schema(
        request=AdminUpdateSerializer,
        responses=AdminDetailSerializer,
        description="Update an admin user's information",
        tags=["Admin Management"],
    ),
    delete=extend_schema(
        description="Delete an admin user from Keycloak",
        responses={204: None},
        tags=["Admin Management"],
    ),
)
class AdminDetailView(RoleRequiredMixin, APIView):
    """
    View for retrieving, updating, and deleting individual admin users.
    Requires 'general_admin' role.
    """

    def get(self, request, user_id):
        """Retrieve an admin user by ID."""
        try:
            admin = admin_service.get_admin(user_id)
            serializer = AdminDetailSerializer(admin)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeycloakError as e:
            return Response(
                {"error": "Failed to retrieve admin", "detail": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

    @require_roles_class_method("general_admin")
    def put(self, request, user_id):
        """Update an admin user."""
        serializer = AdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            admin = admin_service.update_admin(
                user_id=user_id,
                email=serializer.validated_data.get("email"),
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                enabled=serializer.validated_data.get("enabled"),
                nucleos=serializer.validated_data.get("nucleos", None),
            )
            response_serializer = AdminDetailSerializer(admin)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except KeycloakError as e:
            return Response(
                {"error": "Failed to update admin", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @require_roles_class_method("general_admin")
    def delete(self, request, user_id):
        """Delete an admin user."""
        try:
            admin_service.delete_admin(user_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeycloakError as e:
            return Response(
                {"error": "Failed to delete admin", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    request=AdminPasswordChangeSerializer,
    responses={200: {"description": "Password changed successfully"}},
    description="Change an admin user's password",
    tags=["Admin Management"],
)
class AdminPasswordChangeView(RoleRequiredMixin, APIView):
    """
    View for changing an admin user's password.
    Requires 'general_admin' role.
    """

    @require_roles_class_method("general_admin")
    def post(self, request, user_id):
        """Change an admin user's password."""
        serializer = AdminPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            admin_service.change_password(
                user_id=user_id,
                new_password=serializer.validated_data["new_password"],
                temporary=serializer.validated_data.get("temporary", False),
            )

            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK,
            )

        except KeycloakError as e:
            return Response(
                {"error": "Failed to change password", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


urlpatterns = [
    path("", AdminListCreateView.as_view(), name="admin-list-create"),
    path("<str:user_id>/", AdminDetailView.as_view(), name="admin-detail"),
    path(
        "<str:user_id>/password/",
        AdminPasswordChangeView.as_view(),
        name="admin-password",
    ),
]
