"""
Course management views
"""

from admin_api.utils.decorators import (
    RoleRequiredMixin,
    require_roles,
    require_roles_class_method,
)
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CourseAddToSeasonSerializer,
    CourseCreateSerializer,
    CourseDetailQuerySerializer,
    CourseDetailSerializer,
    CourseListQuerySerializer,
    CourseListSerializer,
    CourseRemoveFromSeasonSerializer,
    CourseUpdateSerializer,
)
from .service import course_service


@extend_schema_view(
    get=extend_schema(
        parameters=[CourseListQuerySerializer],
        responses=CourseListSerializer(many=True),
        description="List all courses with optional search",
        tags=["Course Management"],
    ),
    post=extend_schema(
        request=CourseCreateSerializer,
        responses=CourseDetailSerializer,
        description="Create a new course",
        tags=["Course Management"],
    ),
)
class CourseListCreateView(RoleRequiredMixin, APIView):
    def get(self, request: Request):
        serializer = CourseListQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        courses = course_service.list_courses(
            admin_id=str(request.user_id) if "nucleo_admin" in request.roles else None,
            season_id=request.query_params.get("season_id"),
        )

        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def post(self, request: Request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = course_service.create_course(
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
            nucleo_id=str(serializer.validated_data["nucleo_id"]),
        )

        serializer = CourseDetailSerializer(course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        parameters=[CourseDetailQuerySerializer],
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
class CourseDetailView(RoleRequiredMixin, APIView):

    def get(self, request, course_id):
        serializer = CourseDetailQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        course = course_service.get_course(
            course_id, season_id=serializer.validated_data.get("season_id")
        )

        serializer = CourseDetailSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def put(self, request, course_id):
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = course_service.update_course(
            course_id,
            name=serializer.validated_data.get("name"),
            abbreviation=serializer.validated_data.get("abbreviation"),
            nucleo_id=(
                str(serializer.validated_data.get("nucleo_id"))
                if serializer.validated_data.get("nucleo_id")
                else None
            ),
        )

        serializer = CourseDetailSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def delete(self, request, course_id):
        course_service.delete_course(course_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=CourseAddToSeasonSerializer,
    responses=CourseDetailSerializer,
    description="Add a course to a season",
    tags=["Course Management"],
)
@api_view(["POST"])
@require_roles("general_admin")
def add_course_to_season(request: Request, course_id):
    serializer = CourseAddToSeasonSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    course = course_service.add_to_season(
        course_id, season_id=serializer.validated_data["season_id"]
    )

    serializer = CourseDetailSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=CourseRemoveFromSeasonSerializer,
    responses=CourseDetailSerializer,
    description="Remove a course from a season",
    tags=["Course Management"],
)
@api_view(["POST"])
@require_roles("general_admin")
def remove_course_from_season(request: Request, course_id):
    serializer = CourseRemoveFromSeasonSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    course = course_service.remove_from_season(
        course_id, season_id=serializer.validated_data["season_id"]
    )

    serializer = CourseDetailSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("", CourseListCreateView.as_view(), name="course-list"),
    path("<uuid:course_id>/", CourseDetailView.as_view(), name="course-detail"),
    path(
        "<uuid:course_id>/add_to_season/",
        add_course_to_season,
        name="course-add-to-season",
    ),
    path(
        "<uuid:course_id>/remove_from_season/",
        remove_course_from_season,
        name="course-remove-from-season",
    ),
]
