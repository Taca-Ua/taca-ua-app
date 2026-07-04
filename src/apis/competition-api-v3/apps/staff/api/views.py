from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin

from ..selectors import get_staff_by_id, get_staff_table
from ..service import create_staff, delete_staff, update_staff
from .serializers import (
    StaffCreateSerializer,
    StaffDetailSerializer,
    StaffListSerializer,
    StaffUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List all staff members",
        description="Retrieve a list of all staff members.",
        tags=["Staff Management"],
        responses={200: StaffListSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create a new staff member",
        description="Create a new staff member with the provided details.",
        tags=["Staff Management"],
        request=StaffCreateSerializer,
        responses={201: StaffDetailSerializer},
    ),
)
class StaffListCreateView(RoleRequiredMixin, APIView):

    def get(self, request):
        staff_members = get_staff_table()

        serializer = StaffListSerializer(staff_members, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff = create_staff(
            name=serializer.validated_data["name"],
            staff_number=serializer.validated_data.get("staff_number"),
            contact=serializer.validated_data.get("contact"),
        )

        serializer = StaffDetailSerializer(get_staff_by_id(staff.id))
        return Response(serializer.data, status=201)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a staff member",
        description="Get details of a specific staff member by ID.",
        tags=["Staff Management"],
        responses={200: StaffDetailSerializer},
    ),
    put=extend_schema(
        summary="Update a staff member",
        description="Update details of a specific staff member by ID.",
        tags=["Staff Management"],
        request=StaffUpdateSerializer,
        responses={200: StaffDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete a staff member",
        description="Delete a specific staff member by ID.",
        tags=["Staff Management"],
        responses={204: None},
    ),
)
class StaffDetailView(RoleRequiredMixin, APIView):

    def get(self, request, staff_id):
        staff = get_staff_by_id(staff_id)

        serializer = StaffDetailSerializer(staff)
        return Response(serializer.data)

    def put(self, request, staff_id):
        serializer = StaffUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff = update_staff(
            staff_id=staff_id,
            name=serializer.validated_data.get("name"),
            staff_number=serializer.validated_data.get("staff_number"),
            contact=serializer.validated_data.get("contact"),
        )

        serializer = StaffDetailSerializer(get_staff_by_id(staff.id))
        return Response(serializer.data)

    def delete(self, request, staff_id):
        delete_staff(staff_id)
        return Response(status=204)


urlpatterns = [
    path("", StaffListCreateView.as_view(), name="staff-list-create"),
    path("<uuid:staff_id>/", StaffDetailView.as_view(), name="staff-detail"),
]
