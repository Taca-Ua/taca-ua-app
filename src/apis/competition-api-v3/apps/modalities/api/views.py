import logging

from apps.utils import count_queries
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin, require_roles_class_method
from shared.auth.utils import RolesEnum

from .. import service as modality_service
from ..selectors import get_modalities_table, get_modality_by_id
from .filters import ModalityQuerySerializer
from .serializers import (
    ModalityAddToSeasonSerializer,
    ModalityCreateSerializer,
    ModalityDetailSerializer,
    ModalityListSerializer,
    ModalityUpdateSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    get=extend_schema(
        summary="List Modalities",
        description="Retrieve a list of all modalities.",
        tags=["Modalities Management"],
        responses={200: ModalityListSerializer(many=True)},
        parameters=[ModalityQuerySerializer],
    ),
    post=extend_schema(
        summary="Create Modality",
        description="Create a new modality.",
        tags=["Modalities Management"],
        parameters=[ModalityQuerySerializer],
        request=ModalityCreateSerializer,
        responses={201: ModalityListSerializer},
    ),
)
class ModalityListCreateView(RoleRequiredMixin, APIView):
    @count_queries
    def get(self, request):
        serializer = ModalityQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modalities = get_modalities_table(
            season_id=serializer.validated_data.get("season_id")
        )

        serializer = ModalityListSerializer(modalities, many=True)
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request):
        request_serializer = ModalityCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        params_serializer = ModalityQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)

        modality = modality_service.create_modality(
            name=request_serializer.validated_data["name"],
            modality_type_id=request_serializer.validated_data["modality_type_id"],
        )

        logger.info(
            "Created modality",
            extra={"modality_id": modality.id, "modality_name": modality.name},
        )
        serializer = ModalityListSerializer(
            get_modality_by_id(
                modality_id=modality.id,
                season_id=params_serializer.validated_data.get("season_id"),
            )
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Modality",
        description="Retrieve details of a specific modality.",
        tags=["Modalities Management"],
        responses={200: ModalityDetailSerializer},
        parameters=[ModalityQuerySerializer],
    ),
    put=extend_schema(
        summary="Update Modality",
        description="Update details of a specific modality.",
        tags=["Modalities Management"],
        request=ModalityUpdateSerializer,
        responses={200: ModalityDetailSerializer},
        parameters=[ModalityQuerySerializer],
    ),
)
class ModalityDetailView(RoleRequiredMixin, APIView):
    @count_queries
    def get(self, request, modality_id):
        serializer = ModalityQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modality = get_modality_by_id(
            modality_id=modality_id,
            season_id=serializer.validated_data.get("season_id"),
        )

        serializer = ModalityDetailSerializer(modality)
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, modality_id):
        # Validate request body
        req_serializer = ModalityUpdateSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        # Validate query parameters
        params_serializer = ModalityQuerySerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        season_id = params_serializer.validated_data.get("season_id")

        # Update the modality using the service layer
        modality = modality_service.update_modality(
            modality_id=modality_id,
            name=req_serializer.validated_data.get("name"),
            modality_type_id=req_serializer.validated_data.get("modality_type_id"),
        )

        # Render the updated modality and return the response
        logger.info(
            "Updated modality",
            extra={"modality_id": modality.id, "modality_name": modality.name},
        )
        serializer = ModalityDetailSerializer(
            get_modality_by_id(modality_id=modality.id, season_id=season_id)
        )
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        summary="Add Modality to Season",
        description="Add an existing modality to a season.",
        tags=["Modalities Management"],
        request=ModalityAddToSeasonSerializer,
        responses={200: ModalityDetailSerializer},
    ),
    put=extend_schema(
        summary="Remove Modality from Season",
        description="Remove an existing modality from a season.",
        tags=["Modalities Management"],
        responses={200: ModalityDetailSerializer},
    ),
)
class ModalityEditFromSeasonView(RoleRequiredMixin, APIView):
    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request, modality_id, season_id):
        req_serializer = ModalityAddToSeasonSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        modality = modality_service.add_modality_to_season(
            modality_id=modality_id,
            season_id=season_id,
            modality_type_id=req_serializer.validated_data["modality_type_id"],
        )

        serializer = ModalityDetailSerializer(
            get_modality_by_id(modality_id=modality.id, season_id=season_id)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, modality_id, season_id):
        modality = modality_service.remove_modality_from_season(
            modality_id=modality_id, season_id=season_id
        )

        serializer = ModalityDetailSerializer(
            get_modality_by_id(modality_id=modality.id, season_id=season_id)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("", ModalityListCreateView.as_view(), name="modality-list-create"),
    path("<uuid:modality_id>/", ModalityDetailView.as_view(), name="modality-detail"),
    path(
        "<uuid:modality_id>/season/<int:season_id>/",
        ModalityEditFromSeasonView.as_view(),
        name="modality-edit-season",
    ),
]
