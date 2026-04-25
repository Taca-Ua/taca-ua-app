"""
Course management views
"""

from admin_api.utils.decorators import RoleRequiredMixin, require_roles_class_method
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)
from .service import course_service


@extend_schema_view(
    get=extend_schema(
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

        # TODO: This is a temporary solution to handle the case where the request does not have roles (e.g., when using API clients that do not set roles). In the future, we should ensure that all requests have roles properly set.
        request.roles = [] if hasattr(request, "roles") is False else request.roles
        courses = course_service.list_courses(
            admin_id=str(request.user_id) if "nucleo_admin" in request.roles else None
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
        course = course_service.get_course(course_id)
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


urlpatterns = [
    path("", CourseListCreateView.as_view(), name="course-list"),
    path("<uuid:course_id>/", CourseDetailView.as_view(), name="course-detail"),
]
