"""
Regulation management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    RegulationCreateSerializer,
    RegulationListSerializer,
    RegulationUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=RegulationListSerializer(many=True),
        description="List all regulations",
        tags=["Regulation Management"],
    ),
    post=extend_schema(
        request=RegulationCreateSerializer,
        responses=RegulationListSerializer,
        description="Upload a new regulation",
        tags=["Regulation Management"],
    ),
)
class RegulationListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "title": "Regulamento Futebol",
                "description": "Regras do futebol TACA",
                "modality_id": 1,
                "file_url": "http://example.com/reg1.pdf",
                "created_at": "2025-01-15T10:00:00Z",
            },
            {
                "id": 2,
                "title": "Regulamento Futsal",
                "description": "Regras do futsal TACA",
                "modality_id": 2,
                "file_url": "http://example.com/reg2.pdf",
                "created_at": "2025-01-20T10:00:00Z",
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = RegulationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": 3,
            "title": serializer.validated_data.get("title"),
            "description": serializer.validated_data.get("description", ""),
            "modality_id": serializer.validated_data.get("modality_id"),
            "file_url": "http://example.com/reg3.pdf",
            "created_at": "2025-12-01T12:00:00Z",
        }
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=RegulationListSerializer,
        description="Get a single regulation by ID",
        tags=["Regulation Management"],
    ),
    put=extend_schema(
        request=RegulationUpdateSerializer,
        responses=RegulationListSerializer,
        description="Update regulation metadata",
        tags=["Regulation Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a regulation",
        tags=["Regulation Management"],
    ),
)
class RegulationDetailView(APIView):
    def get(self, request, regulation_id):
        # Mock data for testing - find the regulation by ID
        all_regulations = [
            {
                "id": 1,
                "title": "Regulamento Futebol",
                "description": "Regras do futebol TACA",
                "modality_id": 1,
                "file_url": "http://example.com/reg1.pdf",
                "created_at": "2025-01-15T10:00:00Z",
            },
            {
                "id": 2,
                "title": "Regulamento Futsal",
                "description": "Regras do futsal TACA",
                "modality_id": 2,
                "file_url": "http://example.com/reg2.pdf",
                "created_at": "2025-01-20T10:00:00Z",
            },
        ]

        regulation = next(
            (r for r in all_regulations if r["id"] == regulation_id), None
        )

        if regulation is None:
            return Response(
                {"error": "Regulation not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(regulation)

    def put(self, request, regulation_id):
        serializer = RegulationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": regulation_id,
            "title": serializer.validated_data.get(
                "title", f"Regulation {regulation_id}"
            ),
            "description": serializer.validated_data.get("description", ""),
            "modality_id": serializer.validated_data.get("modality_id"),
            "file_url": f"http://example.com/reg{regulation_id}.pdf",
            "created_at": "2025-12-01T12:00:00Z",
        }
        return Response(dummy_response)

    def delete(self, request, regulation_id):
        return Response(status=status.HTTP_204_NO_CONTENT)
