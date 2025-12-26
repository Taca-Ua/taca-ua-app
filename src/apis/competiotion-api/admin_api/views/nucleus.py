"""
Modality management views
"""

from datetime import datetime, timezone

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Nucleo
from ..serializers import (
    NucleosCreateSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
)


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
        nucleos = Nucleo.objects.all()
        return Response(
            [
                {
                    "id": str(nucleo.id),
                    "name": nucleo.name,
                    "abbreviation": nucleo.abbreviation,
                }
                for nucleo in nucleos
            ]
        )

    def post(self, request: Request):
        serializer = NucleosCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nucleo = Nucleo.objects.create(
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
            created_by=request.user.id or "00000000-0000-0000-0000-000000000000",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        nucleo.save()
        return Response(
            {
                "id": str(nucleo.id),
                "name": nucleo.name,
                "abbreviation": nucleo.abbreviation,
            },
            status=status.HTTP_201_CREATED,
        )


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
        nucleo = Nucleo.objects.filter(id=nucleo_id).first()
        if not nucleo:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "id": str(nucleo.id),
                "name": nucleo.name,
                "abbreviation": nucleo.abbreviation,
                "created_by": str(nucleo.created_by),
                "updated_at": nucleo.updated_at,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, nucleo_id):
        serializer = NucleosUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get nucleo
        nucleo = Nucleo.objects.filter(id=nucleo_id).first()
        if not nucleo:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # update fields
        if "name" in serializer.validated_data:
            nucleo.name = serializer.validated_data["name"]
        if "abbreviation" in serializer.validated_data:
            nucleo.abbreviation = serializer.validated_data["abbreviation"]
        nucleo.updated_at = datetime.now(timezone.utc)
        nucleo.save()

        return Response(
            {
                "id": str(nucleo.id),
                "name": nucleo.name,
                "abbreviation": nucleo.abbreviation,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, nucleo_id):
        nucleo = Nucleo.objects.filter(id=nucleo_id).first()
        if not nucleo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        nucleo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
