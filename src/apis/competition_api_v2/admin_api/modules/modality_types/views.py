"""
Modality management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ModalityTypeCreateSerializer,
    ModalityTypeDetailSerializer,
    ModalityTypeListSerializer,
    ModalityTypeMinimalSerializer,
    ModalityTypeUpdateSerializer,
)
from .service import modality_types_service


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeListSerializer(many=True),
        description="List all modality types",
        tags=["Modality Ttype Management"],
    ),
    post=extend_schema(
        request=ModalityTypeCreateSerializer,
        responses=ModalityTypeListSerializer,
        description="Create a new modality type",
        tags=["Modality Ttype Management"],
    ),
)
class ModalityTypeListCreateView(APIView):

    def get(self, request: Request):
        modality_types = modality_types_service.list_modality_types(
            include_playoff=True
        )

        serializer = ModalityTypeListSerializer(modality_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        serializer = ModalityTypeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = modality_types_service.create_modality_type(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            escaloes=serializer.validated_data["escaloes"],
            is_playoff=serializer.validated_data.get("is_playoff", False),
        )
        serializer = ModalityTypeListSerializer(modality_type)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=ModalityTypeDetailSerializer,
        description="Get a modality by ID",
        tags=["Modality Ttype Management"],
    ),
    put=extend_schema(
        request=ModalityTypeUpdateSerializer,
        responses=ModalityTypeDetailSerializer,
        description="Update a modality",
        tags=["Modality Ttype Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a modality",
        tags=["Modality Ttype Management"],
    ),
)
class ModalityTypeDetailView(APIView):
    def get(self, request, modality_type_id):
        modality_type = modality_types_service.get_modality_type(modality_type_id)

        serializer = ModalityTypeDetailSerializer(modality_type)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, modality_type_id):
        serializer = ModalityTypeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        modality_type = modality_types_service.update_modality_type(
            modality_type_id,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
            escaloes=serializer.validated_data.get("escaloes"),
            is_playoff=serializer.validated_data.get("is_playoff"),
        )

        serializer = ModalityTypeDetailSerializer(modality_type)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, modality_type_id):
        modality_types_service.delete_modality_type(modality_type_id)
        return Response(
            {"detail": "Modality type deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    responses={200: ModalityTypeMinimalSerializer(many=True)},
    description="List all modality types with minimal information",
    tags=["Modality Ttype Management"],
)
@api_view(["GET"])
def list_modality_types(request: Request):
    modality_types = modality_types_service.list_modality_types(include_playoff=False)
    serializer = ModalityTypeMinimalSerializer(modality_types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path(
        "",
        ModalityTypeListCreateView.as_view(),
        name="modality-type-list-create",
    ),
    path(
        "minimal/",
        list_modality_types,
        name="modality-type-list-minimal",
    ),
    path(
        "<uuid:modality_type_id>/",
        ModalityTypeDetailView.as_view(),
        name="modality-type-detail",
    ),
]
