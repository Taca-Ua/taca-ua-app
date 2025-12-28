"""
Modality management views
"""

from datetime import datetime, timezone

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ModalityType
from ..serializers import (
    ModalityTypeCreateSerializer,
    ModalityTypeDetailSerializer,
    ModalityTypeListSerializer,
    ModalityTypeUpdateSerializer,
)


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
        modality_types = ModalityType.objects.all()

        modality_types_data = ModalityTypeListSerializer(modality_types, many=True).data

        return Response(modality_types_data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        serializer = ModalityTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = ModalityType.objects.create(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            escaloes=serializer.validated_data["escaloes"],
            created_by="00000000-0000-0000-0000-000000000000",  # Placeholder UUID
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return Response(
            {
                "id": modality_type.id,
                "name": modality_type.name,
                "description": modality_type.description,
                "escaloes": modality_type.escaloes,
            },
            status=status.HTTP_201_CREATED,
        )


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

        modality_type = ModalityType.objects.get(id=modality_type_id)
        print(modality_type)

        return Response(
            {
                "id": modality_type.id,
                "name": modality_type.name,
                "description": modality_type.description,
                "escaloes": modality_type.escaloes,
                "created_by": modality_type.created_by,
                "created_at": modality_type.created_at,
                "updated_at": modality_type.updated_at,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, modality_type_id):
        serializer = ModalityTypeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = ModalityType.objects.get(id=modality_type_id)
        modality_type.name = serializer.validated_data.get("name", modality_type.name)
        modality_type.description = serializer.validated_data.get(
            "description", modality_type.description
        )
        modality_type.escaloes = serializer.validated_data.get(
            "escaloes", modality_type.escaloes
        )
        modality_type.updated_at = datetime.now(timezone.utc)
        modality_type.save()

        return Response(
            {
                "id": modality_type.id,
                "name": modality_type.name,
                "description": modality_type.description,
                "escaloes": modality_type.escaloes,
                "created_by": modality_type.created_by,
                "created_at": modality_type.created_at,
                "updated_at": modality_type.updated_at,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, modality_type_id):
        modality_type = ModalityType.objects.get(id=modality_type_id)
        modality_type.delete()

        return Response(
            {"detail": "Modality type deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
