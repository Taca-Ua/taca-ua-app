"""
Student management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators import RoleRequiredMixin
from ..serializers.students import (
    StudentCreateSerializer,
    StudentDetailSerializer,
    StudentListRequestSerializer,
    StudentListSerializer,
    StudentMembershipSyncSerializer,
    StudentUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


@extend_schema_view(
    get=extend_schema(
        parameters=[StudentListRequestSerializer],
        responses=StudentListSerializer(many=True),
        description="List students of the authenticated nucleo (filtered by course_id)",
        tags=["Student Management"],
    ),
    post=extend_schema(
        request=StudentCreateSerializer,
        responses=StudentListSerializer,
        description="Create a new student for the authenticated nucleo",
        tags=["Student Management"],
    ),
)
class StudentListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        serializer = StudentListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        all_students = modalities_service_client.list_students(
            admin_id=request.user_id if "nucleo_admin" in request.roles else None,
        )

        serializer = StudentListSerializer(all_students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = modalities_service_client.create_student(
            full_name=serializer.validated_data["full_name"],
            student_number=serializer.validated_data["student_number"],
            is_member=serializer.validated_data.get("is_member", False),
            course_id=str(serializer.validated_data["course_id"]),
        )

        serializer = StudentListSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=StudentDetailSerializer,
        description="Update or delete a student",
        tags=["Student Management"],
    ),
    put=extend_schema(
        request=StudentUpdateSerializer,
        responses=StudentDetailSerializer,
        description="Update or delete a student",
        tags=["Student Management"],
    ),
    delete=extend_schema(
        description="Delete a student",
        responses={204: None},
        tags=["Student Management"],
    ),
)
class StudentDetailView(RoleRequiredMixin, APIView):
    def get(self, request, student_id):
        student = modalities_service_client.get_student(student_id)

        serializer = StudentDetailSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, student_id):
        serializer = StudentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = modalities_service_client.update_student(
            student_id,
            full_name=serializer.validated_data.get("full_name"),
            course_id=serializer.validated_data.get("course_id"),
            student_number=serializer.validated_data.get("student_number"),
            is_member=serializer.validated_data.get("is_member"),
        )

        serializer = StudentDetailSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, student_id):
        modalities_service_client.delete_student(student_id)
        return Response(
            {"detail": "Student deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    post=extend_schema(
        request=StudentMembershipSyncSerializer,
        responses={200: dict},
        description=(
            "Reset o estado de sócio de todos os participantes no âmbito (núcleo ou global) "
            "e define como sócio os NMECs enviados."
        ),
        tags=["Student Management"],
    ),
)
class StudentMembershipSyncView(RoleRequiredMixin, APIView):
    def post(self, request):
        serializer = StudentMembershipSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admin_id = (
            str(request.user_id) if "nucleo_admin" in request.roles else None
        )
        result = modalities_service_client.sync_student_membership(
            student_numbers=serializer.validated_data.get("student_numbers") or [],
            admin_id=admin_id,
        )
        return Response(result, status=status.HTTP_200_OK)


urlpatterns = [
    path(
        "sync-membership/",
        StudentMembershipSyncView.as_view(),
        name="student-membership-sync",
    ),
    path("", StudentListCreateView.as_view(), name="student-list"),
    path("<uuid:student_id>/", StudentDetailView.as_view(), name="student-detail"),
]
