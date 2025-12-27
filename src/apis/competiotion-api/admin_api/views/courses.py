"""
Course management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


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
        courses = modalities_service_client.list_courses()
        return Response(courses, status=status.HTTP_200_OK)

    def post(self, request: Request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = modalities_service_client.create_course(
            {
                "name": serializer.validated_data["name"],
                "abbreviation": serializer.validated_data["abbreviation"],
                "nucleo_id": str(serializer.validated_data["nucleo_id"]),
            }
        )

        return Response(course, status=status.HTTP_201_CREATED)


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
        course = modalities_service_client.get_course(course_id)
        return Response(course)

    def put(self, request, course_id):
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_data = {}
        if serializer.validated_data.get("name", None) is not None:
            update_data["name"] = serializer.validated_data["name"]
        if serializer.validated_data.get("abbreviation", None) is not None:
            update_data["abbreviation"] = serializer.validated_data["abbreviation"]
        if serializer.validated_data.get("nucleo_id", None) is not None:
            update_data["nucleo_id"] = str(serializer.validated_data["nucleo_id"])

        course = modalities_service_client.update_course(course_id, update_data)
        return Response(course)

    def delete(self, request, course_id):
        modalities_service_client.delete_course(course_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
