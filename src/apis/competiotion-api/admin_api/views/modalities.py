"""
Modality management views
"""

from datetime import datetime, timezone

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

        modality_type_ids = [modality.modality_type_id for modality in modalities]
        modality_types = ModalityType.objects.filter(id__in=modality_type_ids)
        modality_type_dict = {mt.id: mt.name for mt in modality_types}

        return Response(
            [
                {
                    "id": str(modality.id),
                    "name": modality.name,
                    "modality_type": modality_type_dict.get(
                        modality.modality_type_id, None
                    ),
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

        modality = Modality.objects.create(
            name=serializer.validated_data["name"],
            modality_type_id=serializer.validated_data.get("modality_type_id", None),
            created_by=request.user.id or "00000000-0000-0000-0000-000000000000",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        modality.save()

        return Response(
            {
                "id": str(modality.id),
                "name": modality.name,
                "modality_type": modality_type.name if modality_type else None,
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

        modality_type = ModalityType.objects.filter(
            id=modality.modality_type_id
        ).first()

        return Response(
            {
                "id": str(modality.id),
                "name": modality.name,
                "modality_type": modality_type.name if modality_type else None,
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

        # validate modality_type_id if provided
        modality_type = None
        if serializer.validated_data.get("modality_type_id", None) is not None:
            modality_type = ModalityType.objects.filter(
                id=serializer.validated_data["modality_type_id"]
            ).first()
            if not modality_type:
                return Response(
                    {"error": "Invalid modality_type_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # update modality
        modality.name = serializer.validated_data.get("name", modality.name)
        modality.modality_type_id = serializer.validated_data.get(
            "modality_type_id", modality.modality_type_id
        )
        modality.updated_at = datetime.now(timezone.utc)
        modality.save()

        # fetch updated modality_type
        if not modality_type:
            modality_type = ModalityType.objects.filter(
                id=modality.modality_type_id
            ).first()

        return Response(
            {
                "id": str(modality.id),
                "name": modality.name,
                "modality_type": modality_type.name if modality_type else None,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, modality_id):
        modality = Modality.objects.filter(id=modality_id).first()
        if not modality:
            return Response(status=status.HTTP_404_NOT_FOUND)

        modality.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
