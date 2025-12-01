"""
Modality management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    ModalityCreateSerializer,
    ModalityListSerializer,
    ModalityUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityListSerializer(many=True),
        description="List all modalities",
        tags=["Modality Management"],
    ),
    post=extend_schema(
        request=ModalityCreateSerializer,
        responses=ModalityListSerializer,
        description="Create a new modality",
        tags=["Modality Management"],
    ),
)
class ModalityListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "name": "Futebol",
                "type": "coletiva",
                "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
            },
            {
                "id": 2,
                "name": "Futsal",
                "type": "coletiva",
                "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
            },
            {
                "id": 3,
                "name": "Ténis",
                "type": "individual",
                "scoring_schema": {"win": 2, "loss": 0},
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=ModalityUpdateSerializer,
        responses=ModalityListSerializer,
        description="Update a modality",
        tags=["Modality Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a modality",
        tags=["Modality Management"],
    ),
)
class ModalityDetailView(APIView):
    def put(self, request, modality_id):
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": modality_id,
            "name": serializer.validated_data.get("name", f"Modality {modality_id}"),
            "type": serializer.validated_data.get("type", "coletiva"),
            "scoring_schema": serializer.validated_data.get(
                "scoring_schema", {"win": 3, "draw": 1, "loss": 0}
            ),
        }
        return Response(dummy_response)

    def delete(self, request, modality_id):
        return Response(status=status.HTTP_204_NO_CONTENT)
