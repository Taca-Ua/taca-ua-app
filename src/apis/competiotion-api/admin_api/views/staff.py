from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.staff import (
    StaffCreateSerializer,
    StaffDetailSerializer,
    StaffListSerializer,
    StaffUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


@extend_schema_view(
    get=extend_schema(
        responses=StaffListSerializer(many=True),
        description="List staff of the authenticated nucleo (filtered by staff_number)",
        tags=["Staff Management"],
    ),
    post=extend_schema(
        request=StaffCreateSerializer,
        responses=StaffListSerializer,
        description="Create a new staff member for the authenticated nucleo",
        tags=["Staff Management"],
    ),
)
class StaffListCreateView(APIView):
    def get(self, request):
        all_staff = modalities_service_client.list_staff()

        serializer = StaffListSerializer(all_staff, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff_member = modalities_service_client.create_staff(
            full_name=serializer.validated_data["full_name"],
            staff_number=serializer.validated_data.get("staff_number", None),
            contact=serializer.validated_data.get("contact", None),
        )

        serializer = StaffListSerializer(staff_member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=StaffDetailSerializer,
        description="Update a staff member of the authenticated nucleo",
        tags=["Staff Management"],
    ),
    put=extend_schema(
        request=StaffUpdateSerializer,
        responses=StaffDetailSerializer,
        description="Update a staff member of the authenticated nucleo",
        tags=["Staff Management"],
    ),
    delete=extend_schema(
        description="Delete a staff member of the authenticated nucleo",
        responses={204: None},
        tags=["Staff Management"],
    ),
)
class StaffDetailView(APIView):
    def get(self, request, staff_id):
        staff_member = modalities_service_client.get_staff(staff_id)

        serializer = StaffDetailSerializer(staff_member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, staff_id):
        serializer = StaffUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff_member = modalities_service_client.update_staff(
            staff_id, serializer.validated_data
        )

        serializer = StaffDetailSerializer(staff_member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, staff_id):
        modalities_service_client.delete_staff(staff_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", StaffListCreateView.as_view(), name="staff-list"),
    path("<uuid:staff_id>/", StaffDetailView.as_view(), name="staff-detail"),
]
