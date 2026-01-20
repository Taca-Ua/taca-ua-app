"""
Student management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.students import (
    StudentCreateSerializer,
    StudentDetailSerializer,
    StudentListRequestSerializer,
    StudentListSerializer,
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
class StudentListCreateView(APIView):
    def get(self, request):
        serializer = StudentListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        all_students = modalities_service_client.list_students()

        serializer = StudentListSerializer(all_students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = modalities_service_client.create_student(
            {
                "full_name": serializer.validated_data["full_name"],
                "student_number": serializer.validated_data["student_number"],
                "is_member": serializer.validated_data.get("is_member", False),
                "course_id": str(serializer.validated_data["course_id"]),
            }
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
class StudentDetailView(APIView):
    def get(self, request, student_id):
        student = modalities_service_client.get_student(student_id)

        serializer = StudentDetailSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, student_id):
        serializer = StudentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_data = {}
        if "full_name" in serializer.validated_data:
            update_data["full_name"] = serializer.validated_data["full_name"]
        if "course_id" in serializer.validated_data:
            update_data["course_id"] = str(serializer.validated_data["course_id"])
        if "student_number" in serializer.validated_data:
            update_data["student_number"] = serializer.validated_data["student_number"]
        if "is_member" in serializer.validated_data:
            update_data["is_member"] = serializer.validated_data["is_member"]

        student = modalities_service_client.update_student(student_id, update_data)

        serializer = StudentDetailSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, student_id):
        modalities_service_client.delete_student(student_id)
        return Response(
            {"detail": "Student deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


urlpatterns = [
    path("", StudentListCreateView.as_view(), name="student-list"),
    path("<uuid:student_id>/", StudentDetailView.as_view(), name="student-detail"),
]
