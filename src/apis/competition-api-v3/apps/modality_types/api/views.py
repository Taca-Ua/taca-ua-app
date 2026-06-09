from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import (
    RoleRequiredMixin,
    require_auth,
    require_roles_class_method,
)
from shared.auth.utils import RolesEnum

from .. import service as modality_type_service
from ..selectors import get_modality_type_by_id, get_modality_types_table
from .filters import ModalityTypeFilterSerializer
from .serializers import (
    ModalityTypeCreateSerializer,
    ModalityTypeDetailSerializer,
    ModalityTypeListMinimalSerializer,
    ModalityTypeListSerializer,
    ModalityTypeUpdateSerializer,
)


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
class ModalityTypeListCreateView(RoleRequiredMixin, APIView):

    def get(self, request):
        serializer = ModalityTypeFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modality_types = get_modality_types_table(
            season_id=serializer.validated_data.get("season_id")
        )

        serializer = ModalityTypeListSerializer(modality_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
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

        serializer = ModalityTypeListSerializer(
            get_modality_type_by_id(modality_type.id)
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeDetailSerializer,
        summary="Retrieve a modality type",
        description="Get details of a specific modality type by its ID.",
        tags=["Modality Types"],
    ),
    put=extend_schema(
        request=ModalityTypeUpdateSerializer,
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
class ModalityTypeDetailView(RoleRequiredMixin, APIView):
    def get(self, request, modality_type_id):

        modality_type = get_modality_type_by_id(modality_type_id)

        serializer = ModalityTypeDetailSerializer(modality_type)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, modality_type_id):
        serializer = ModalityTypeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = modality_type_service.update_modality_type(
            modality_type_id=modality_type_id,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
            escaloes_data=serializer.validated_data.get("escaloes"),
        )

        serializer = ModalityTypeDetailSerializer(
            get_modality_type_by_id(modality_type.id)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def delete(self, request, modality_type_id):
        modality_type_service.delete_modality_type(modality_type_id)

        return Response(
            {"message": "Modality type deleted"},
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
class ModalityTypeListView(RoleRequiredMixin, APIView):

    @require_auth
    def get(self, request):
        serializer = ModalityTypeFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        modality_types = get_modality_types_table(
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
