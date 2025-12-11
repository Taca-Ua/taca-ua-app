"""
Course management views
"""

from datetime import datetime, timezone

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Course, Nucleo
from ..serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=CourseListSerializer(many=True),
        description="List all courses with optional search",
        tags=["Course Management"],
    ),
    post=extend_schema(
        request=CourseCreateSerializer,
        responses=CourseListSerializer,
        description="Create a new course",
        tags=["Course Management"],
    ),
)
class CourseListCreateView(APIView):
    def get(self, request: Request):
        courses = Course.objects.all()
        return Response(
            [
                {
                    "id": course.id,
                    "name": course.name,
                    "abbreviation": course.abbreviation,
                    "nucleo": course.nucleo.name,
                    "created_at": course.created_at,
                }
                for course in courses
            ],
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # validate nucleo existence
        nucleo = Nucleo.objects.filter(
            id=serializer.validated_data["nucleo_id"]
        ).first()
        if not nucleo:
            return Response(
                {"detail": "Nucleo not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        course = Course.objects.create(
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
            nucleo=nucleo,
            created_by=request.user.id or "00000000-0000-0000-0000-000000000000",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return Response(
            {
                "id": course.id,
                "name": course.name,
                "abbreviation": course.abbreviation,
                "nucleo": course.nucleo.name,
                "created_at": course.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        responses=CourseDetailSerializer,
        description="Get a course by ID",
        tags=["Course Management"],
    ),
    put=extend_schema(
        request=CourseUpdateSerializer,
        responses=CourseDetailSerializer,
        description="Update a course",
        tags=["Course Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a course and all associated teams and students",
        tags=["Course Management"],
    ),
)
class CourseDetailView(APIView):
    def get(self, request, course_id):
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": course.id,
                "name": course.name,
                "abbreviation": course.abbreviation,
                "nucleo": course.nucleo.name,
                "created_at": course.created_at,
            }
        )

    def put(self, request, course_id):
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get course
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # update fields
        if serializer.validated_data.get("name", None) is not None:
            course.name = serializer.validated_data["name"]

        if serializer.validated_data.get("abbreviation", None) is not None:
            course.abbreviation = serializer.validated_data["abbreviation"]

        if serializer.validated_data.get("nucleo_id", None) is not None:
            nucleo = Nucleo.objects.filter(
                id=serializer.validated_data["nucleo_id"]
            ).first()
            if not nucleo:
                return Response(
                    {"detail": "Nucleo not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            course.nucleo = nucleo

        course.save()

        return Response(
            {
                "id": course.id,
                "name": course.name,
                "abbreviation": course.abbreviation,
                "nucleo": course.nucleo.name,
                "created_at": course.created_at,
            }
        )

    def delete(self, request, course_id):
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
