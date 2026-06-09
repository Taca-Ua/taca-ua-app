from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import (
    RoleRequiredMixin,
    require_roles,
    require_roles_class_method,
)
from shared.auth.utils import RolesEnum

from ..selectors import get_course_by_id, get_courses_table
from ..service import add_course_to_season as service_add_course_to_season
from ..service import create_course, delete_course
from ..service import remove_course_from_season as service_remove_course_from_season
from ..service import update_course
from .filters import CourseSeasonParamSerializer
from .serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List Courses",
        description="Retrieve a list of courses.",
        tags=["Course Manegement"],
        parameters=[CourseSeasonParamSerializer],
        responses={200: CourseListSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create Course",
        description="Create a new course.",
        tags=["Course Manegement"],
        parameters=[CourseSeasonParamSerializer],
        request=CourseCreateSerializer,
        responses={201: CourseListSerializer},
    ),
)
class CourseListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        serializer = CourseSeasonParamSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        courses = get_courses_table(
            season_id=serializer.validated_data.get("season_id")
        )

        serializer = CourseListSerializer(
            courses,
            many=True,
        )
        return Response(serializer.data, status=200)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request):
        req_serializer = CourseCreateSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        param_serializer = CourseSeasonParamSerializer(data=request.query_params)
        param_serializer.is_valid(raise_exception=True)

        course = create_course(
            name=req_serializer.validated_data["name"],
            abbreviation=req_serializer.validated_data["abbreviation"],
            nucleo_id=req_serializer.validated_data["nucleo_id"],
        )

        serializer = CourseListSerializer(
            get_course_by_id(
                course_id=course.id,
                season_id=param_serializer.validated_data.get("season_id"),
            )
        )
        return Response(serializer.data, status=201)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Course",
        description="Retrieve details of a specific course.",
        tags=["Course Manegement"],
        parameters=[CourseSeasonParamSerializer],
        responses={200: CourseDetailSerializer},
    ),
    put=extend_schema(
        summary="Update Course",
        description="Update details of a specific course.",
        tags=["Course Manegement"],
        parameters=[CourseSeasonParamSerializer],
        request=CourseUpdateSerializer,
        responses={200: CourseDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete Course",
        description="Delete a specific course.",
        tags=["Course Manegement"],
        responses={204: "No Content"},
    ),
)
class CourseDetailView(APIView):
    def get(self, request, course_id):
        serializer = CourseSeasonParamSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        course = get_course_by_id(
            course_id=course_id, season_id=serializer.validated_data.get("season_id")
        )

        serializer = CourseDetailSerializer(course)
        return Response(serializer.data, status=200)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, course_id):
        req_serializer = CourseUpdateSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        param_serializer = CourseSeasonParamSerializer(data=request.query_params)
        param_serializer.is_valid(raise_exception=True)

        updated_course = update_course(
            course_id=course_id,
            name=req_serializer.validated_data.get("name"),
            abbreviation=req_serializer.validated_data.get("abbreviation"),
            nucleo_id=req_serializer.validated_data.get("nucleo_id"),
        )

        serializer = CourseDetailSerializer(
            get_course_by_id(
                course_id=updated_course.id,
                season_id=param_serializer.validated_data.get("season_id"),
            )
        )
        return Response(serializer.data, status=200)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def delete(self, request, course_id):
        delete_course(course_id=course_id)
        return Response(status=204)


@extend_schema(
    summary="Remove Course from Season",
    description="Remove a course from a season.",
    tags=["Course Manegement"],
    parameters=[CourseSeasonParamSerializer],
    responses={200: CourseDetailSerializer},
)
@api_view(["PUT"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def remove_course_from_season(request, course_id, season_id):
    serializer = CourseSeasonParamSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    course = service_remove_course_from_season(course_id=course_id, season_id=season_id)

    serializer = CourseDetailSerializer(
        get_course_by_id(
            course_id=course.id, season_id=serializer.validated_data.get("season_id")
        )
    )
    return Response(serializer.data, status=200)


@extend_schema(
    summary="Add Course to Season",
    description="Add a course to a season.",
    tags=["Course Manegement"],
    parameters=[CourseSeasonParamSerializer],
    responses={200: CourseDetailSerializer},
)
@api_view(["PUT"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def add_course_to_season(request, course_id, season_id):
    serializer = CourseSeasonParamSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    course = service_add_course_to_season(course_id=course_id, season_id=season_id)

    serializer = CourseDetailSerializer(
        get_course_by_id(
            course_id=course.id, season_id=serializer.validated_data.get("season_id")
        )
    )
    return Response(serializer.data, status=200)


urlpatterns = [
    path("", CourseListCreateView.as_view(), name="course-list"),
    path("<uuid:course_id>/", CourseDetailView.as_view(), name="course-detail"),
    path(
        "<uuid:course_id>/add_to_season/<int:season_id>/",
        add_course_to_season,
        name="course-add-to-season",
    ),
    path(
        "<uuid:course_id>/remove_from_season/<int:season_id>/",
        remove_course_from_season,
        name="course-remove-from-season",
    ),
]
