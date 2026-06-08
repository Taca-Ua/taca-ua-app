from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin, require_roles_class_method
from shared.auth.utils import RolesEnum

from ..queries import get_admin_by_id, list_admins
from ..service import change_admin_password, create_admin, delete_admin, update_admin
from .filters import AdminListFilter
from .renders import render_admin_detail, render_admin_list
from .serializers import (
    AdminCreateSerializer,
    AdminDetailSerializer,
    AdminListSerializer,
    AdminPasswordChangeSerializer,
    AdminUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=AdminListSerializer(many=True),
        description="List all admin users with 'general_admin' or 'admin_nucleo' roles",
        tags=["Admin Management"],
        parameters=[AdminListFilter],
    ),
    post=extend_schema(
        request=AdminCreateSerializer,
        responses={201: AdminListSerializer},
        description="Create a new admin user in Keycloak with the specified role",
        tags=["Admin Management"],
    ),
)
class AdminListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        serializer = AdminListFilter(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        admins = list_admins(include=serializer.validated_data.get("include_inactive"))

        serializer = AdminListSerializer(render_admin_list(admins), many=True)
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request):
        serializer = AdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admin = create_admin(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            name=serializer.validated_data["name"],
            role=serializer.validated_data["role"],
            nucleos=serializer.validated_data.get("nucleos"),
        )

        serializer = AdminListSerializer(render_admin_list(admin).get())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

    def get(self, request, user_id):
        """Retrieve an admin user by ID."""
        admin = get_admin_by_id(user_id=user_id).get()

        serializer = AdminDetailSerializer(render_admin_detail(admin).first())
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, user_id):
        """Update an admin user."""
        serializer = AdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admin = update_admin(
            user_id=user_id,
            email=serializer.validated_data["email"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            enabled=serializer.validated_data["enabled"],
            nucleos=serializer.validated_data["nucleos"],
        )

        serializer = AdminDetailSerializer(render_admin_detail(admin).first())
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def delete(self, request, user_id):
        """Delete an admin user."""
        delete_admin(user_id=user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=AdminPasswordChangeSerializer,
    responses={200: {"description": "Password changed successfully"}},
    description="Change an admin user's password",
    tags=["Admin Management"],
)
class AdminPasswordChangeView(RoleRequiredMixin, APIView):

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request, user_id):
        """Change an admin user's password."""
        serializer = AdminPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        change_admin_password(
            user_id=user_id,
            new_password=serializer.validated_data["new_password"],
        )

        return Response(
            {"detail": "Password changed successfully"}, status=status.HTTP_200_OK
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
