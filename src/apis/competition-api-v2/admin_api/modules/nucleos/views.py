"""
Nucleo management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    NucleosCreateSerializer,
    NucleosDetailSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
)
from .service import nucleos_service


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
        nucleos = nucleos_service.list_nucleos()

        # Serialize output data
        serializer = NucleosListSerializer(nucleos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        # Serialize input data
        serializer = NucleosCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nucleo = nucleos_service.create_nucleo(
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
        )

        # Serialize output data
        serializer = NucleosListSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=NucleosDetailSerializer,
        description="Get a nucleo by ID",
        tags=["Nucleo Management"],
    ),
    put=extend_schema(
        request=NucleosUpdateSerializer,
        responses=NucleosDetailSerializer,
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
        nucleo = nucleos_service.get_nucleo(nucleo_id)

        # Serialize output data
        serializer = NucleosDetailSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, nucleo_id):
        # Serialize input data
        serializer = NucleosUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nucleo = nucleos_service.update_nucleo(
            nucleo_id,
            name=serializer.validated_data.get("name"),
            abbreviation=serializer.validated_data.get("abbreviation"),
        )

        # Serialize output data
        serializer = NucleosDetailSerializer(nucleo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, nucleo_id):
        nucleos_service.delete_nucleo(nucleo_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", NucleoListCreateView.as_view(), name="nucleo-list"),
    path("<uuid:nucleo_id>/", NucleoDetailView.as_view(), name="nucleo-detail"),
]
