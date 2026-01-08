"""
Modality management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.nucleus import (
    NucleosCreateSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


@extend_schema_view(
    get=extend_schema(
        responses=NucleosListSerializer(many=True),
        description="List all nucleos",
        tags=["Nucleo Management"],
    ),
    post=extend_schema(
        request=NucleosCreateSerializer,
        responses=NucleosListSerializer,
        description="Create a new nucleo",
        tags=["Nucleo Management"],
    ),
)
class NucleoListCreateView(APIView):
    def get(self, request: Request):
        nucleos = modalities_service_client.list_nucleos()
        return Response(nucleos)

    def post(self, request: Request):
        serializer = NucleosCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nucleo = modalities_service_client.create_nucleo(
            {
                "name": serializer.validated_data["name"],
                "abbreviation": serializer.validated_data["abbreviation"],
            }
        )
        return Response(nucleo, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=NucleosListSerializer,
        description="Get a nucleo by ID",
        tags=["Nucleo Management"],
    ),
    put=extend_schema(
        request=NucleosUpdateSerializer,
        responses=NucleosListSerializer,
        description="Update a nucleo",
        tags=["Nucleo Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a nucleo",
        tags=["Nucleo Management"],
    ),
)
class NucleoDetailView(APIView):
    def get(self, request, nucleo_id):
        nucleo = modalities_service_client.get_nucleo(nucleo_id)
        return Response(nucleo, status=status.HTTP_200_OK)

    def put(self, request, nucleo_id):
        serializer = NucleosUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_data = {}
        if "name" in serializer.validated_data:
            update_data["name"] = serializer.validated_data["name"]
        if "abbreviation" in serializer.validated_data:
            update_data["abbreviation"] = serializer.validated_data["abbreviation"]

        nucleo = modalities_service_client.update_nucleo(nucleo_id, update_data)
        return Response(nucleo, status=status.HTTP_200_OK)

    def delete(self, request, nucleo_id):
        modalities_service_client.delete_nucleo(nucleo_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", NucleoListCreateView.as_view(), name="nucleo-list"),
    path("<uuid:nucleo_id>/", NucleoDetailView.as_view(), name="nucleo-detail"),
]
