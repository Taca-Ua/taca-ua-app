"""
Modality management views
"""

from admin_api.utils.decorators import RoleRequiredMixin, require_roles_class_method
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ModalityCreateSerializer,
    ModalityListQuerySerializer,
    ModalitySerializer,
    ModalityUpdateSerializer,
)
from .service import modalities_service


# Views
@extend_schema_view(
    get=extend_schema(
        parameters=[ModalityListQuerySerializer],
        responses=ModalitySerializer(many=True),
        description="List all modalities",
        tags=["Modality Management"],
    ),
    post=extend_schema(
        request=ModalityCreateSerializer,
        responses=ModalitySerializer,
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

        serializer = ModalitySerializer(modalities, many=True)
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
        response_serializer = ModalitySerializer(modality)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
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
        modality = modalities_service.get_modality(modality_id)

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
        )

        response_serializer = ModalitySerializer(modality)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def delete(self, request, modality_id):
        modalities_service.delete_modality(modality_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


# URL patterns
urlpatterns = [
    path("", ModalityListCreateView.as_view(), name="modality-list-create"),
    path("<uuid:modality_id>/", ModalityDetailView.as_view(), name="modality-detail"),
]
