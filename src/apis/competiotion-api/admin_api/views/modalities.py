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
from ..services.modalities_service import modalities_service_client


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
        modalities = modalities_service_client.list_modalities()
        return Response(modalities)

    def post(self, request: Request):
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality = modalities_service_client.create_modality(
            {
                "name": serializer.validated_data["name"],
                "modality_type_id": str(
                    serializer.validated_data.get("modality_type_id")
                ),
            }
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
        modality = modalities_service_client.get_modality(modality_id)
        return Response(modality, status=status.HTTP_200_OK)

    def put(self, request, modality_id):
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_data = {}
        if serializer.validated_data.get("name", None) is not None:
            update_data["name"] = serializer.validated_data["name"]
        if serializer.validated_data.get("modality_type_id", None) is not None:
            update_data["modality_type_id"] = str(
                serializer.validated_data["modality_type_id"]
            )

        modality = modalities_service_client.update_modality(modality_id, update_data)
        return Response(modality, status=status.HTTP_200_OK)

    def delete(self, request, modality_id):
        modalities_service_client.delete_modality(modality_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
