"""
Modality management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ModalityCreateSerializer,
    ModalitySerializer,
    ModalityUpdateSerializer,
)


# Views
@extend_schema_view(
    get=extend_schema(
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
class ModalityListCreateView(APIView):
    def get(self, request: Request):
        return Response(
            {"detail": "Listing modalities is not implemented yet."},
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request):
        # Serialize input data
        serializer = ModalityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Modality created successfully."}, status=status.HTTP_201_CREATED
        )


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
class ModalityDetailView(APIView):
    def get(self, request, modality_id):
        return Response(
            {"detail": "Getting modality details is not implemented yet."},
            status=status.HTTP_200_OK,
        )

    def put(self, request, modality_id):
        # Serialize input data
        serializer = ModalityUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Modality updated successfully."}, status=status.HTTP_200_OK
        )

    def delete(self, request, modality_id):
        return Response(
            {"detail": "Modality deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


# URL patterns
urlpatterns = [
    path("", ModalityListCreateView.as_view(), name="modality-list-create"),
    path("<uuid:modality_id>/", ModalityDetailView.as_view(), name="modality-detail"),
]
