"""
Modality management views
"""

from datetime import datetime, timezone

from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Modality, ModalityType
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
    def get(self, request: Request):
        modalities = Modality.objects.all()

        return Response(
            [
                {
                    "id": str(modality.id),
                    "name": modality.name,
                    "modality_type": modality.modality_type.name,
                }
                for modality in modalities
            ]
        )

    def post(self, request: Request):
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # validate modality_type_id if provided
        modality_type = ModalityType.objects.filter(
            id=serializer.validated_data.get("modality_type_id", None)
        ).first()
        if not modality_type:
            return Response(
                {"error": "Invalid modality_type_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            modality = Modality.objects.create(
                name=serializer.validated_data["name"],
                modality_type=modality_type,
                created_by=getattr(request.user, "id")
                or "00000000-0000-0000-0000-000000000000",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            modality.save()
        except IntegrityError as e:
            return Response(
                {"error": f"Integrity error creating modality: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create modality: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "id": str(modality.id),
                "name": modality.name,
                "modality_type": modality.modality_type.name,
            },
            status=status.HTTP_201_CREATED,
        )


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
        modality = Modality.objects.filter(id=modality_id).first()
        if not modality:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "id": str(modality.id),
                "name": modality.name,
                "modality_type": modality.modality_type.name,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, modality_id):
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get modality
        modality = Modality.objects.filter(id=modality_id).first()
        if not modality:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # update fields if provided
        if serializer.validated_data.get("name", None) is not None:
            modality.name = serializer.validated_data["name"]

        if serializer.validated_data.get("modality_type_id", None) is not None:
            modality_type = ModalityType.objects.filter(
                id=serializer.validated_data["modality_type_id"]
            ).first()

            if not modality_type:
                return Response(
                    {"error": "Invalid modality_type_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            modality.modality_type = modality_type

        # update timestamp
        modality.updated_at = datetime.now(timezone.utc)
        modality.save()

        return Response(
            {
                "id": str(modality.id),
                "name": modality.name,
                "modality_type": modality.modality_type.name,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, modality_id):
        modality = Modality.objects.filter(id=modality_id).first()
        if not modality:
            return Response(status=status.HTTP_404_NOT_FOUND)

        modality.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
