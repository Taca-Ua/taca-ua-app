"""
Course management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    CourseCreateSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=CourseListSerializer(many=True),
        description="List all courses",
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
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "name": "Engenharia de Computadores e Telemática",
                "short_code": "MECT",
                "color": "#FF5733",
            },
            {
                "id": 2,
                "name": "Engenharia Informática",
                "short_code": "LEI",
                "color": "#33FF57",
            },
            {
                "id": 3,
                "name": "Engenharia Eletrónica e Telecomunicações",
                "short_code": "MIEET",
                "color": "#3357FF",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=CourseUpdateSerializer,
        responses=CourseListSerializer,
        description="Update a course",
        tags=["Course Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a course",
        tags=["Course Management"],
    ),
)
class CourseDetailView(APIView):
    def put(self, request, course_id):
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": course_id,
            "name": serializer.validated_data.get("name", f"Course {course_id}"),
            "short_code": serializer.validated_data.get("short_code", f"C{course_id}"),
            "color": serializer.validated_data.get("color", "#000000"),
        }
        return Response(dummy_response)

    def delete(self, request, course_id):
        return Response(status=status.HTTP_204_NO_CONTENT)
