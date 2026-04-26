"""
Athlete management views
"""

from admin_api.utils.decorators import RoleRequiredMixin
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AthleteCreateSerializer,
    AthleteDetailSerializer,
    AthleteListRequestSerializer,
    AthleteListSerializer,
    AthleteMembershipSyncSerializer,
    AthleteUpdateSerializer,
)
from .service import athletes_service


@extend_schema_view(
    get=extend_schema(
        parameters=[AthleteListRequestSerializer],
        responses=AthleteListSerializer(many=True),
        description="List students of the authenticated nucleo (filtered by course_id)",
        tags=["Athlete Management"],
    ),
    post=extend_schema(
        request=AthleteCreateSerializer,
        responses=AthleteListSerializer,
        description="Create a new student for the authenticated nucleo",
        tags=["Athlete Management"],
    ),
)
class AthleteListCreateView(RoleRequiredMixin, APIView):

    def get(self, request):
        serializer = AthleteListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        all_students = athletes_service.list_athletes(
            course_id=(
                str(serializer.validated_data.get("course_id"))
                if serializer.validated_data.get("course_id")
                else None
            ),
            team_id=(
                str(serializer.validated_data.get("team_id"))
                if serializer.validated_data.get("team_id")
                else None
            ),
            admin_id=str(request.user_id) if "nucleo_admin" in request.roles else None,
        )

        serializer = AthleteListSerializer(all_students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AthleteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = athletes_service.create_student(
            full_name=serializer.validated_data["full_name"],
            student_number=serializer.validated_data["student_number"],
            is_member=serializer.validated_data.get("is_member", False),
            course_id=str(serializer.validated_data["course_id"]),
        )

        serializer = AthleteListSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=AthleteDetailSerializer,
        description="Update or delete a student",
        tags=["Athlete Management"],
    ),
    put=extend_schema(
        request=AthleteUpdateSerializer,
        responses=AthleteDetailSerializer,
        description="Update or delete a student",
        tags=["Athlete Management"],
    ),
    delete=extend_schema(
        description="Delete a student",
        responses={204: None},
        tags=["Athlete Management"],
    ),
)
class AthleteDetailView(RoleRequiredMixin, APIView):

    def get(self, request, student_id):
        student = athletes_service.get_student(student_id)

        serializer = AthleteDetailSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, student_id):
        serializer = AthleteUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = athletes_service.update_student(
            student_id,
            full_name=serializer.validated_data.get("full_name"),
            course_id=(
                str(serializer.validated_data.get("course_id"))
                if serializer.validated_data.get("course_id")
                else None
            ),
            student_number=serializer.validated_data.get("student_number"),
            is_member=serializer.validated_data.get("is_member"),
        )

        serializer = AthleteDetailSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, student_id):
        athletes_service.delete_student(student_id)
        return Response(
            {"detail": "Athlete deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    post=extend_schema(
        request=AthleteMembershipSyncSerializer,
        responses={200: dict},
        description=(
            "Reset o estado de sócio de todos os participantes no âmbito (núcleo ou global) "
            "e define como sócio os NMECs enviados."
        ),
        tags=["Athlete Management"],
    ),
)
class AthleteMembershipSyncView(RoleRequiredMixin, APIView):

    def post(self, request):
        serializer = AthleteMembershipSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admin_id = str(request.user_id) if "nucleo_admin" in request.roles else None
        result = athletes_service.sync_student_membership(
            student_numbers=serializer.validated_data.get("student_numbers") or [],
            admin_id=admin_id,
        )
        return Response(result, status=status.HTTP_200_OK)


urlpatterns = [
    path("", AthleteListCreateView.as_view(), name="student-list"),
    path(
        "sync-membership/",
        AthleteMembershipSyncView.as_view(),
        name="student-membership-sync",
    ),
    # Detail view should be after list view to avoid URL conflicts
    path("<uuid:student_id>/", AthleteDetailView.as_view(), name="student-detail"),
]
