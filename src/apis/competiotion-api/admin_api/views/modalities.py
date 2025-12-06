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

# Mock database for modalities
MOCK_MODALITIES = {
    1: {
        "id": 1,
        "name": "Futebol",
        "type": "coletiva",
        "year": "25/26",
        "description": "Futebol de campo 11v11",
        "scoring_schema": '{"win": 3, "draw": 1, "loss": 0}',
    },
    2: {
        "id": 2,
        "name": "Futsal",
        "type": "coletiva",
        "year": "25/26",
        "description": "Futebol de salão 5v5",
        "scoring_schema": '{"win": 3, "draw": 1, "loss": 0}',
    },
    3: {
        "id": 3,
        "name": "Basquetebol",
        "type": "coletiva",
        "year": "25/26",
        "description": "Basquetebol 5v5",
        "scoring_schema": '{"win": 2, "loss": 0}',
    },
    4: {
        "id": 4,
        "name": "Voleibol",
        "type": "coletiva",
        "year": "25/26",
        "description": "Voleibol 6v6",
        "scoring_schema": '{"win": 2, "loss": 0}',
    },
    5: {
        "id": 5,
        "name": "Andebol",
        "type": "coletiva",
        "year": "25/26",
        "description": "Andebol 7v7",
        "scoring_schema": '{"win": 2, "loss": 0}',
    },
    6: {
        "id": 6,
        "name": "Rugby",
        "type": "coletiva",
        "year": "24/25",
        "description": "Rugby 15v15",
        "scoring_schema": '{"win": 4, "loss": 0}',
    },
}


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
        modalities = list(MOCK_MODALITIES.values())
        return Response(modalities)

    def post(self, request):
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate new ID
        max_id = max(MOCK_MODALITIES.keys()) if MOCK_MODALITIES else 0
        new_id = max_id + 1

        new_modality = {
            "id": new_id,
            **serializer.validated_data,
        }

        MOCK_MODALITIES[new_id] = new_modality
        return Response(new_modality, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityListSerializer,
        description="Get a modality by ID",
        tags=["Modality Management"],
    ),
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
    def get(self, request, modality_id):
        if modality_id not in MOCK_MODALITIES:
            return Response(
                {"error": "Modality not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(MOCK_MODALITIES[modality_id])

    def put(self, request, modality_id):
        if modality_id not in MOCK_MODALITIES:
            return Response(
                {"error": "Modality not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update existing modality
        modality = MOCK_MODALITIES[modality_id]
        for key, value in serializer.validated_data.items():
            modality[key] = value

        return Response(modality)

    def delete(self, request, modality_id):
        if modality_id not in MOCK_MODALITIES:
            return Response(
                {"error": "Modality not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        del MOCK_MODALITIES[modality_id]
        return Response(status=status.HTTP_204_NO_CONTENT)
