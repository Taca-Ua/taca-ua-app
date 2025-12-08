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
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Mock database of all students and technical staff
        all_students = [
            # MECT Students (course_id: 1)
            {
                "id": 1,
                "course_id": 1,
                "full_name": "João Silva",
                "student_number": "100001",
                "email": "joao.silva@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 2,
                "course_id": 1,
                "full_name": "Maria Santos",
                "student_number": "100002",
                "email": "maria.santos@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 3,
                "course_id": 1,
                "full_name": "Carlos Oliveira",
                "student_number": "100003",
                "email": "carlos.oliveira@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 4,
                "course_id": 1,
                "full_name": "Ana Costa",
                "student_number": "100004",
                "email": "ana.costa@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 5,
                "course_id": 1,
                "full_name": "Pedro Ferreira",
                "student_number": "100005",
                "email": "pedro.ferreira@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 11,
                "course_id": 1,
                "full_name": "Ricardo Almeida",
                "student_number": "100011",
                "email": "ricardo.almeida@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 12,
                "course_id": 1,
                "full_name": "Sofia Rodrigues",
                "student_number": "100012",
                "email": "sofia.rodrigues@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 13,
                "course_id": 1,
                "full_name": "Miguel Pereira",
                "student_number": "100013",
                "email": "miguel.pereira@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 14,
                "course_id": 1,
                "full_name": "Beatriz Martins",
                "student_number": "100014",
                "email": "beatriz.martins@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 15,
                "course_id": 1,
                "full_name": "Tiago Fernandes",
                "student_number": "100015",
                "email": "tiago.fernandes@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 24,
                "course_id": 1,
                "full_name": "Prof. José Costa",
                "student_number": "STAFF001",
                "email": "jose.costa@ua.pt",
                "is_member": True,
                "member_type": "technical_staff",
            },
            {
                "id": 25,
                "course_id": 1,
                "full_name": "Treinador António Silva",
                "student_number": "STAFF002",
                "email": "antonio.silva@ua.pt",
                "is_member": True,
                "member_type": "technical_staff",
            },
            # LEI Students (course_id: 2)
            {
                "id": 6,
                "course_id": 2,
                "full_name": "Luís Gomes",
                "student_number": "200001",
                "email": "luis.gomes@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 7,
                "course_id": 2,
                "full_name": "Inês Carvalho",
                "student_number": "200002",
                "email": "ines.carvalho@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 8,
                "course_id": 2,
                "full_name": "André Pinto",
                "student_number": "200003",
                "email": "andre.pinto@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 9,
                "course_id": 2,
                "full_name": "Catarina Lopes",
                "student_number": "200004",
                "email": "catarina.lopes@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 10,
                "course_id": 2,
                "full_name": "Bruno Sousa",
                "student_number": "200005",
                "email": "bruno.sousa@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 21,
                "course_id": 2,
                "full_name": "Diogo Ribeiro",
                "student_number": "200006",
                "email": "diogo.ribeiro@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 22,
                "course_id": 2,
                "full_name": "Mariana Silva",
                "student_number": "200007",
                "email": "mariana.silva@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 23,
                "course_id": 2,
                "full_name": "Gonçalo Santos",
                "student_number": "200008",
                "email": "goncalo.santos@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 26,
                "course_id": 2,
                "full_name": "Prof. Manuel Ferreira",
                "student_number": "STAFF003",
                "email": "manuel.ferreira@ua.pt",
                "is_member": True,
                "member_type": "technical_staff",
            },
            # LECI Students (course_id: 3)
            {
                "id": 16,
                "course_id": 3,
                "full_name": "Rita Fernandes",
                "student_number": "300001",
                "email": "rita.fernandes@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 17,
                "course_id": 3,
                "full_name": "Francisco Nunes",
                "student_number": "300002",
                "email": "francisco.nunes@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 18,
                "course_id": 3,
                "full_name": "Carolina Dias",
                "student_number": "300003",
                "email": "carolina.dias@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 19,
                "course_id": 3,
                "full_name": "Rui Monteiro",
                "student_number": "300004",
                "email": "rui.monteiro@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 20,
                "course_id": 3,
                "full_name": "Joana Teixeira",
                "student_number": "300005",
                "email": "joana.teixeira@ua.pt",
                "is_member": True,
                "member_type": "student",
            },
            {
                "id": 27,
                "course_id": 3,
                "full_name": "Prof. Isabel Lopes",
                "student_number": "STAFF004",
                "email": "isabel.lopes@ua.pt",
                "is_member": True,
                "member_type": "technical_staff",
            },
        ]

        # Filter students by user's course_id
        filtered_students = [
            student
            for student in all_students
            if student["course_id"] == user["course_id"]
        ]

        return Response(filtered_students)

    def post(self, request):
        # Get authenticated user
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = StudentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Auto-assign the student to the authenticated user's course
        dummy_response = {
            "id": 20,
            "course_id": user["course_id"],
            **serializer.validated_data,
        }
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema(
    request=StudentUpdateSerializer,
    responses=StudentListSerializer,
    description="Update or delete a student",
    tags=["Student Management"],
)
@api_view(["PUT", "DELETE"])
def student_detail(request, student_id):
    if request.method == "PUT":
        serializer = StudentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": student_id,
            "course_id": 1,
            "full_name": serializer.validated_data.get(
                "full_name", f"Student {student_id}"
            ),
            "student_number": f"10000{student_id}",
            "email": serializer.validated_data.get(
                "email", f"student{student_id}@ua.pt"
            ),
            "is_member": serializer.validated_data.get("is_member", False),
        }
        return Response(dummy_response)

    elif request.method == "DELETE":
        # Get authenticated user
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # In production, verify the student belongs to the user's course
        # For now, just return success
        return Response(status=status.HTTP_204_NO_CONTENT)
