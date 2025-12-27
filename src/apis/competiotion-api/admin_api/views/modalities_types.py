"""
Modality management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    ModalityTypeCreateSerializer,
    ModalityTypeDetailSerializer,
    ModalityTypeListSerializer,
    ModalityTypeUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeListSerializer(many=True),
        description="List all modality types",
        tags=["Modality Management"],
    ),
    post=extend_schema(
        request=ModalityTypeCreateSerializer,
        responses=ModalityTypeListSerializer,
        description="Create a new modality type",
        tags=["Modality Management"],
    ),
)
class ModalityTypeListCreateView(APIView):
    def get(self, request: Request):
        modality_types = modalities_service_client.list_modality_types()
        return Response(modality_types, status=status.HTTP_200_OK)

    def post(self, request: Request):
        serializer = ModalityTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = modalities_service_client.create_modality_type(
            {
                "name": serializer.validated_data["name"],
                "description": serializer.validated_data.get("description", ""),
                "escaloes": serializer.validated_data["escaloes"],
            }
        )

        return Response(modality_type, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeDetailSerializer,
        description="Get a modality by ID",
        tags=["Modality Management"],
    ),
    put=extend_schema(
        request=ModalityTypeUpdateSerializer,
        responses=ModalityTypeDetailSerializer,
        description="Update a modality",
        tags=["Modality Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a modality",
        tags=["Modality Management"],
    ),
)
class ModalityTypeDetailView(APIView):
    def get(self, request, modality_type_id):
        modality_type = modalities_service_client.get_modality_type(modality_type_id)
        return Response(modality_type, status=status.HTTP_200_OK)

    def put(self, request, modality_type_id):
        serializer = ModalityTypeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_data = {}
        if "name" in serializer.validated_data:
            update_data["name"] = serializer.validated_data["name"]
        if "description" in serializer.validated_data:
            update_data["description"] = serializer.validated_data["description"]
        if "escaloes" in serializer.validated_data:
            update_data["escaloes"] = serializer.validated_data["escaloes"]

        modality_type = modalities_service_client.update_modality_type(
            modality_type_id, update_data
        )
        return Response(modality_type, status=status.HTTP_200_OK)

    def delete(self, request, modality_type_id):
        modalities_service_client.delete_modality_type(modality_type_id)
        return Response(
            {"detail": "Modality type deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
