"""
Modality management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    ModalityCreateSerializer,
    ModalityListSerializer,
    ModalityUpdateSerializer,
)
from ..services.modalities_service import ModalitiesService


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
    def get(self, request: Request):
        service = ModalitiesService()

        # Extract filters from query parameters
        type_filter = request.query_params.get("type")
        limit = request.query_params.get("limit", 50)
        offset = request.query_params.get("offset", 0)

        modalities = service.list_modalities(
            type=type_filter, limit=int(limit), offset=int(offset)
        )

        return Response(modalities["modalities"])

    def post(self, request: Request):
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ModalitiesService()

        modality = service.create_modality(
            name=serializer.validated_data["name"],
            type=serializer.validated_data["type"],
            created_by=request.user.id or "00000000-0000-0000-0000-000000000000",
            scoring_schema=serializer.validated_data.get("scoring_schema"),
        )

        return Response(modality, status=status.HTTP_201_CREATED)


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
        service = ModalitiesService()
        modality = service.get_modality(modality_id)
        return Response(modality)

    def put(self, request, modality_id):
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ModalitiesService()

        modality = service.update_modality(
            modality_id,
            updated_by=request.user.id or "00000000-0000-0000-0000-000000000000",
            name=serializer.validated_data.get("name"),
            type=serializer.validated_data.get("type"),
            scoring_schema=serializer.validated_data.get("scoring_schema"),
        )

        return Response(modality)

    def delete(self, request, modality_id):
        service = ModalitiesService()
        resp = service.delete_modality(modality_id)

        return Response(resp)
