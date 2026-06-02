import logging

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.utils import get_user

from .. import service as modality_type_service
from ..queries import get_modality_type, list_modality_types
from .filters import ModalityTypeFilterSerializer
from .renders import render_modality_type, render_modality_types
from .serializers import (
    ModalityTypeCreateSerializer,
    ModalityTypeDetailSerializer,
    ModalityTypeListMinimalSerializer,
    ModalityTypeListSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeListSerializer(many=True),
        parameters=[ModalityTypeFilterSerializer],
        summary="List modality types",
        description="Retrieve a list of all modality types.",
        tags=["Modality Types"],
    ),
    post=extend_schema(
        request=ModalityTypeCreateSerializer,
        responses=ModalityTypeListSerializer,
        summary="Create a new modality type",
        description="Create a new modality type with the provided details.",
        tags=["Modality Types"],
    ),
)
class ModalityTypeListCreateView(APIView):

    def get(self, request):
        serializer = ModalityTypeFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modality_types = list_modality_types(
            season_id=serializer.validated_data.get("season_id")
        )

        serializer = ModalityTypeListSerializer(
            render_modality_types(modality_types), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ModalityTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = modality_type_service.create_modality_type(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description"),
            mode=serializer.validated_data.get("mode"),
            tournament_competitor_type=serializer.validated_data.get(
                "tournament_competitor_type"
            ),
            season_id=serializer.validated_data.get("season_id"),
            escaloes_data=serializer.validated_data.get("escaloes", []),
        )

        if modality_type is None:
            return Response(
                {"error": "Failed to create modality type"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user = get_user(request)
        logger.info(
            "Created modality type",
            extra={"modality_type_id": modality_type.id, "user_id": user.user_id},
        )
        serializer = ModalityTypeListSerializer(modality_type)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeDetailSerializer,
        summary="Retrieve a modality type",
        description="Get details of a specific modality type by its ID.",
        tags=["Modality Types"],
    ),
    put=extend_schema(
        request=ModalityTypeCreateSerializer,
        responses=ModalityTypeDetailSerializer,
        summary="Update a modality type",
        description="Update the details of a specific modality type by its ID.",
        tags=["Modality Types"],
    ),
    delete=extend_schema(
        summary="Delete a modality type",
        description="Delete a specific modality type by its ID.",
        tags=["Modality Types"],
    ),
)
class ModalityTypeDetailView(APIView):
    def get(self, request, modality_type_id):

        modality_type = get_modality_type(modality_type_id)

        serializer = ModalityTypeDetailSerializer(
            render_modality_type(modality_type).get()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, modality_type_id):
        serializer = ModalityTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = modality_type_service.update_modality_type(
            modality_type_id=modality_type_id,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
            mode=serializer.validated_data.get("mode"),
            tournament_competitor_type=serializer.validated_data.get(
                "tournament_competitor_type"
            ),
        )

        logger.info(f"Updated modality type {modality_type_id}")
        serializer = ModalityTypeDetailSerializer(modality_type)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, modality_type_id):
        success = modality_type_service.delete_modality_type(modality_type_id)
        if not success:
            return Response(
                {"error": "Failed to delete modality type"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info(f"Deleted modality type {modality_type_id}")
        return Response(
            {"message": f"Modality type {modality_type_id} deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeListMinimalSerializer(many=True),
        parameters=[ModalityTypeFilterSerializer],
        summary="List modality types (minimal)",
        description="Retrieve a list of all modality types with minimal details.",
        tags=["Modality Types"],
    ),
)
class ModalityTypeListView(APIView):

    def get(self, request):
        serializer = ModalityTypeFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modality_types = list_modality_types(
            season_id=serializer.validated_data.get("season_id"),
            mode=serializer.validated_data.get("mode"),
        )

        serializer = ModalityTypeListMinimalSerializer(modality_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("", ModalityTypeListCreateView.as_view(), name="modality-type-list-create"),
    path("minimal/", ModalityTypeListView.as_view(), name="modality-type-list-minimal"),
    path(
        "<uuid:modality_type_id>/",
        ModalityTypeDetailView.as_view(),
        name="modality-type-detail",
    ),
]
