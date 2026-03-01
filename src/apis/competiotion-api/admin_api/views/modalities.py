"""
Modality management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators import RoleRequiredMixin
from ..logging_decorators import log_action
from ..serializers.modalities import (
    ModalityCreateSerializer,
    ModalityDetailSerializer,
    ModalityListSerializer,
    ModalityUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


# Views
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
class ModalityListCreateView(RoleRequiredMixin, APIView):
    @log_action("list_modalities")
    def get(self, request: Request):
        modalities = modalities_service_client.list_modalities()

        # Serialize output data
        serializer = ModalityListSerializer(modalities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @log_action("create_modality")
    def post(self, request: Request):
        # Serialize input data
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create modality via service client
        modality = modalities_service_client.create_modality(
            name=serializer.validated_data["name"],
            modality_type_id=str(serializer.validated_data.get("modality_type_id")),
        )

        # Serialize output data
        serializer = ModalityListSerializer(modality)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityDetailSerializer,
        description="Get a modality by ID",
        tags=["Modality Management"],
    ),
    put=extend_schema(
        request=ModalityUpdateSerializer,
        responses=ModalityDetailSerializer,
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
    @log_action("get_modality")
    def get(self, request, modality_id):
        modality = modalities_service_client.get_modality(modality_id)

        # Serialize output data
        serializer = ModalityDetailSerializer(modality)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @log_action("update_modality")
    def put(self, request, modality_id):
        # Serialize input data
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality = modalities_service_client.update_modality(
            modality_id,
            name=serializer.validated_data.get("name"),
            modality_type_id=str(serializer.validated_data.get("modality_type_id")),
        )

        # Serialize output data
        serializer = ModalityDetailSerializer(modality)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @log_action("delete_modality")
    def delete(self, request, modality_id):
        modalities_service_client.delete_modality(modality_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


# URL patterns
urlpatterns = [
    path("", ModalityListCreateView.as_view(), name="modality-list-create"),
    path("<uuid:modality_id>/", ModalityDetailView.as_view(), name="modality-detail"),
]
