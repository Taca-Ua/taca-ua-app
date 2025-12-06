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

# Mock database for courses
MOCK_COURSES = {
    1: {
        "id": 1,
        "abbreviation": "MECT",
        "name": "Engenharia de Computadores e Telemática",
        "description": "Mestrado em Engenharia de Computadores e Telemática",
        "logo_url": "https://via.placeholder.com/150?text=MECT",
    },
    2: {
        "id": 2,
        "abbreviation": "LEI",
        "name": "Engenharia Informática",
        "description": "Licenciatura em Engenharia Informática",
        "logo_url": "https://via.placeholder.com/150?text=LEI",
    },
    3: {
        "id": 3,
        "abbreviation": "LECI",
        "name": "Engenharia Eletrónica e Telecomunicações",
        "description": "Licenciatura em Engenharia Eletrónica e Telecomunicações",
        "logo_url": "https://via.placeholder.com/150?text=LECI",
    },
    4: {
        "id": 4,
        "abbreviation": "BIOMED",
        "name": "Engenharia Biomédica",
        "description": "Mestrado em Engenharia Biomédica",
        "logo_url": "https://via.placeholder.com/150?text=BIOMED",
    },
    5: {
        "id": 5,
        "abbreviation": "MMAT",
        "name": "Matemática",
        "description": "Mestrado em Matemática",
        "logo_url": "https://via.placeholder.com/150?text=MMAT",
    },
}


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
        courses = list(MOCK_COURSES.values())
        return Response(courses)

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate new ID
        max_id = max(MOCK_COURSES.keys()) if MOCK_COURSES else 0
        new_id = max_id + 1

        # Create new course
        new_course = {"id": new_id, **serializer.validated_data}

        MOCK_COURSES[new_id] = new_course
        return Response(new_course, status=status.HTTP_201_CREATED)


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
        description="Delete a course",
        tags=["Course Management"],
    ),
)
class CourseDetailView(APIView):
    def get(self, request, course_id):
        if course_id not in MOCK_COURSES:
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(MOCK_COURSES[course_id])

    def put(self, request, course_id):
        if course_id not in MOCK_COURSES:
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update existing course
        course = MOCK_COURSES[course_id]
        for key, value in serializer.validated_data.items():
            course[key] = value

        return Response(course)

    def delete(self, request, course_id):
        if course_id not in MOCK_COURSES:
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        del MOCK_COURSES[course_id]
        return Response(status=status.HTTP_204_NO_CONTENT)
