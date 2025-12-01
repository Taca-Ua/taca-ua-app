"""
Student management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    StudentCreateSerializer,
    StudentListSerializer,
    StudentUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=StudentListSerializer(many=True),
        description="List all students of the course",
        tags=["Student Management"],
    ),
    post=extend_schema(
        request=StudentCreateSerializer,
        responses=StudentListSerializer,
        description="Create a new student",
        tags=["Student Management"],
    ),
)
class StudentListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "course_id": 1,
                "full_name": "João Silva",
                "student_number": "100001",
                "email": "joao@ua.pt",
                "is_member": True,
            },
            {
                "id": 2,
                "course_id": 1,
                "full_name": "Maria Santos",
                "student_number": "100002",
                "email": "maria@ua.pt",
                "is_member": True,
            },
            {
                "id": 3,
                "course_id": 2,
                "full_name": "Pedro Costa",
                "student_number": "100003",
                "email": "pedro@ua.pt",
                "is_member": False,
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, "course_id": 1, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema(
    request=StudentUpdateSerializer,
    responses=StudentListSerializer,
    description="Update a student",
    tags=["Student Management"],
)
@api_view(["PUT"])
def student_update(request, student_id):
    serializer = StudentUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "id": student_id,
        "course_id": 1,
        "full_name": serializer.validated_data.get(
            "full_name", f"Student {student_id}"
        ),
        "student_number": f"10000{student_id}",
        "email": serializer.validated_data.get("email", f"student{student_id}@ua.pt"),
        "is_member": serializer.validated_data.get("is_member", False),
    }
    return Response(dummy_response)
