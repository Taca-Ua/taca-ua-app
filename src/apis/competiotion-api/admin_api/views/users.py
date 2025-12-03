"""
User management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    NucleoAdminCreateSerializer,
    NucleoAdminListSerializer,
    NucleoAdminUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=NucleoAdminListSerializer(many=True),
        description="List nucleo administrators",
        tags=["User Management"],
    ),
    post=extend_schema(
        request=NucleoAdminCreateSerializer,
        responses=NucleoAdminListSerializer,
        description="Create nucleo administrator",
        tags=["User Management"],
    ),
)
class NucleoAdminListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "username": "admin_mect",
                "email": "admin@mect.ua.pt",
                "course_id": 1,
                "full_name": "João Silva",
            },
            {
                "id": 2,
                "username": "admin_lei",
                "email": "admin@lei.ua.pt",
                "course_id": 2,
                "full_name": "Maria Santos",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = NucleoAdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 3, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=NucleoAdminUpdateSerializer,
        responses=NucleoAdminListSerializer,
        description="Update nucleo administrator",
        tags=["User Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete nucleo administrator",
        tags=["User Management"],
    ),
)
class NucleoAdminDetailView(APIView):
    def put(self, request, user_id):
        serializer = NucleoAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": user_id,
            "username": f"admin_user_{user_id}",
            "email": f"admin{user_id}@example.pt",
            **serializer.validated_data,
        }
        return Response(dummy_response)

    def delete(self, request, user_id):
        return Response(status=status.HTTP_204_NO_CONTENT)
