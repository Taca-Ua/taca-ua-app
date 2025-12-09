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
    CourseListSerializer,
    CourseUpdateSerializer,
)
from ..services.modalities_service import ModalitiesService


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
        service = ModalitiesService()

        # Extract filters from query parameters
        search = request.query_params.get("search")
        limit = request.query_params.get("limit", 50)
        offset = request.query_params.get("offset", 0)

        courses_data = service.list_courses(
            search=search,
            limit=int(limit),
            offset=int(offset),
        )

        return Response(courses_data["courses"])

    def post(self, request: Request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ModalitiesService()

        course = service.create_course(
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
            created_by=(
                str(request.user.id)
                if request.user.id
                else "00000000-0000-0000-0000-000000000000"
            ),
            description=serializer.validated_data.get("description"),
            logo_url=serializer.validated_data.get("logo_url"),
        )

        return Response(course, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=CourseListSerializer,
        description="Get a course by ID",
        tags=["Course Management"],
    ),
    put=extend_schema(
        request=CourseUpdateSerializer,
        responses=CourseListSerializer,
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
        service = ModalitiesService()
        course = service.get_course(course_id)
        return Response(course)

    def put(self, request, course_id):
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ModalitiesService()

        course = service.update_course(
            course_id=course_id,
            updated_by=(
                str(request.user.id)
                if request.user.id
                else "00000000-0000-0000-0000-000000000000"
            ),
            name=serializer.validated_data.get("name"),
            abbreviation=serializer.validated_data.get("abbreviation"),
            description=serializer.validated_data.get("description"),
            logo_url=serializer.validated_data.get("logo_url"),
        )

        return Response(course)

    def delete(self, request, course_id):
        service = ModalitiesService()
        service.delete_course(course_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
