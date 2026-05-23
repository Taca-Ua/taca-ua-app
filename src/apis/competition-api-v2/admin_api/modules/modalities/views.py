"""
Modality management views
"""

from admin_api.utils.decorators import (
    RoleRequiredMixin,
    require_roles,
    require_roles_class_method,
)
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ModalityCreateSerializer,
    ModalityDetailQuerySerializer,
    ModalityListQuerySerializer,
    ModalityListSerializer,
    ModalityRemoveFromSeasonSerializer,
    ModalitySerializer,
    ModalityUpdateRegulationSerializer,
    ModalityUpdateSerializer,
)
from .service import modalities_service


# Views
@extend_schema_view(
    get=extend_schema(
        parameters=[ModalityListQuerySerializer],
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
class ModalityListCreateView(RoleRequiredMixin, APIView):
    def get(self, request: Request):
        # Serialize query parameters
        serializer = ModalityListQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modalities = modalities_service.list_modalities(
            season_id=serializer.validated_data.get("season_id")
        )

        serializer = ModalityListSerializer(modalities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def post(self, request: Request):
        # Serialize input data
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality = modalities_service.create_modality(
            name=serializer.validated_data["name"],
            modality_type_id=str(serializer.validated_data.get("modality_type_id")),
        )
        response_serializer = ModalityListSerializer(modality)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        parameters=[ModalityDetailQuerySerializer],
        responses=ModalitySerializer,
        description="Get a modality by ID",
        tags=["Modality Management"],
    ),
    put=extend_schema(
        request=ModalityUpdateSerializer,
        responses=ModalitySerializer,
        description="Update a modality",
        tags=["Modality Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a modality",
        tags=["Modality Management"],
    ),
)
class ModalityDetailView(RoleRequiredMixin, APIView):
    def get(self, request, modality_id):
        # Serialize query parameters
        serializer = ModalityDetailQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modality = modalities_service.get_modality(
            modality_id, season_id=serializer.validated_data.get("season_id")
        )

        serializer = ModalitySerializer(modality)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def put(self, request, modality_id):
        # Serialize input data
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality = modalities_service.update_modality(
            modality_id=modality_id,
            name=serializer.validated_data.get("name"),
            modality_type_id=(
                str(serializer.validated_data.get("modality_type_id"))
                if serializer.validated_data.get("modality_type_id")
                else None
            ),
            season_id=serializer.validated_data.get("season_id"),
        )

        response_serializer = ModalitySerializer(modality)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def delete(self, request, modality_id):
        modalities_service.delete_modality(modality_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=ModalityRemoveFromSeasonSerializer,
    responses=ModalitySerializer,
    description="Remove a modality from a season",
    tags=["Modality Management"],
)
@api_view(["PUT"])
@require_roles("general_admin")
def remove_modality_from_season(request, modality_id):
    # Serialize input data
    serializer = ModalityRemoveFromSeasonSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    modality = modalities_service.remove_modality_from_season(
        modality_id=modality_id, season_id=serializer.validated_data["season_id"]
    )

    response_serializer = ModalitySerializer(modality)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=ModalityUpdateRegulationSerializer,
    responses=ModalitySerializer,
    description="Update a modality's regulation for a specific season",
    tags=["Modality Management"],
)
@api_view(["PUT"])
@require_roles("general_admin")
def update_modality_regulation(request, modality_id):
    # Serialize input data
    serializer = ModalityUpdateRegulationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    modality = modalities_service.update_modality_regulation(
        modality_id=str(modality_id),
        season_id=serializer.validated_data["season_id"],
        regulation_id=(
            str(serializer.validated_data["regulation_id"])
            if serializer.validated_data.get("regulation_id")
            else None
        ),
    )

    response_serializer = ModalitySerializer(modality)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


# URL patterns
urlpatterns = [
    path("", ModalityListCreateView.as_view(), name="modality-list-create"),
    path("<uuid:modality_id>/", ModalityDetailView.as_view(), name="modality-detail"),
    path(
        "<uuid:modality_id>/remove-from-season/",
        remove_modality_from_season,
        name="modality-remove-from-season",
    ),
    path(
        "<uuid:modality_id>/update-regulation/",
        update_modality_regulation,
        name="modality-update-regulation",
    ),
]
