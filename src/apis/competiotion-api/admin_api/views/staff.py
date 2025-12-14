from datetime import datetime, timezone

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Staff
from .auth import get_authenticated_user


class StaffListSerializer(serializers.Serializer):
    """Serializer for listing staff"""

    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField()
    staff_number = serializers.CharField()
    contact = serializers.CharField()


class StaffCreateSerializer(serializers.Serializer):
    """Serializer for creating a staff member"""

    full_name = serializers.CharField(required=True)
    staff_number = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)


class StaffUpdateSerializer(serializers.Serializer):
    """Serializer for updating a staff member"""

    full_name = serializers.CharField(required=False)
    staff_number = serializers.CharField(required=False)
    contact = serializers.CharField(required=False)


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
        # Get authenticated user
        # user = get_authenticated_user(request)

        all_staff = Staff.objects.filter()

        return Response(
            [
                {
                    "id": staff.id,
                    "full_name": staff.full_name,
                    "staff_number": staff.staff_number,
                    "contact": staff.contact,
                }
                for staff in all_staff
            ],
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        # Get authenticated user
        user = get_authenticated_user(request)

        serializer = StaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff_member = Staff.objects.create(
            full_name=serializer.validated_data["full_name"],
            staff_number=serializer.validated_data.get("staff_number", None),
            contact=serializer.validated_data.get("contact", None),
            created_by=user or "00000000-0000-0000-0000-000000000000",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return Response(
            {
                "id": staff_member.id,
                "full_name": staff_member.full_name,
                "staff_number": staff_member.staff_number,
                "contact": staff_member.contact,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        request=StaffUpdateSerializer,
        responses=StaffListSerializer,
        description="Update a staff member of the authenticated nucleo",
    ),
    put=extend_schema(
        request=StaffUpdateSerializer,
        responses=StaffListSerializer,
        description="Update a staff member of the authenticated nucleo",
    ),
    delete=extend_schema(
        description="Delete a staff member of the authenticated nucleo",
        responses={204: None},
    ),
)
class StaffDetailView(APIView):
    def put(self, request, staff_id):
        # Get authenticated user
        user = get_authenticated_user(request)

        serializer = StaffUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            staff_member = Staff.objects.get(id=staff_id, nucleo_id=user["nucleo_id"])
        except Staff.DoesNotExist:
            return Response(
                {"detail": "Staff member not found."}, status=status.HTTP_404_NOT_FOUND
            )

        for attr, value in serializer.validated_data.items():
            setattr(staff_member, attr, value)
        staff_member.save()

        return Response(
            {
                "id": staff_member.id,
                "full_name": staff_member.full_name,
                "staff_number": staff_member.staff_number,
                "role": staff_member.role,
            },
            status=status.HTTP_200_OK,
        )
