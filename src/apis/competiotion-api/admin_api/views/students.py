"""
Student management views
"""

from datetime import datetime, timezone

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Course, Student
from ..serializers import (
    StudentCreateSerializer,
    StudentListSerializer,
    StudentUpdateSerializer,
)
from .auth import get_authenticated_user


@extend_schema_view(
    get=extend_schema(
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
        # Get authenticated user
        # user = get_authenticated_user(request)

        all_students = Student.objects.filter()

        return Response(
            [
                {
                    "id": student.id,
                    "course_name": student.course.name,
                    "full_name": student.full_name,
                    "student_number": student.student_number,
                    "is_member": student.is_member,
                }
                for student in all_students
            ],
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        # Get authenticated user
        user = get_authenticated_user(request)

        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print(serializer.validated_data["course_id"])
        course = Course.objects.get(id=serializer.validated_data["course_id"])

        member = Student.objects.create(
            full_name=serializer.validated_data["full_name"],
            student_number=serializer.validated_data["student_number"],
            is_member=serializer.validated_data.get("is_member", False),
            course=course,
            created_by=user or "00000000-0000-0000-0000-000000000000",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return Response(
            {
                "id": member.id,
                "course_name": member.course.name,
                "full_name": member.full_name,
                "student_number": member.student_number,
                "is_member": member.is_member,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        request=StudentUpdateSerializer,
        responses=StudentListSerializer,
        description="Update or delete a student",
        tags=["Student Management"],
    ),
    put=extend_schema(
        request=StudentUpdateSerializer,
        responses=StudentListSerializer,
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
        student = Student.objects.get(id=student_id)

        return Response(
            {
                "id": student.id,
                "course_id": student.course.id,
                "full_name": student.full_name,
                "student_number": student.student_number,
                "is_member": student.is_member,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, student_id):
        serializer = StudentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = Student.objects.get(id=student_id)

        if "full_name" in serializer.validated_data:
            student.full_name = serializer.validated_data["full_name"]
        if "course_id" in serializer.validated_data:
            course = Course.objects.get(id=serializer.validated_data["course_id"])
            student.course = course
        if "student_number" in serializer.validated_data:
            student.student_number = serializer.validated_data["student_number"]
        if "is_member" in serializer.validated_data:
            student.is_member = serializer.validated_data["is_member"]
        student.save()

        return Response(
            {
                "id": student.id,
                "course_id": student.course.id,
                "full_name": student.full_name,
                "student_number": student.student_number,
                "is_member": student.is_member,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, student_id):
        # Get authenticated user
        # user = get_authenticated_user(request)

        student = Student.objects.get(id=student_id)
        student.delete()

        return Response(
            {"detail": "Student deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
