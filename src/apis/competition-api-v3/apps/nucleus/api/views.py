from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin, require_roles_class_method
from shared.auth.utils import RolesEnum

from ..selectors import get_nucleus_by_id, get_nucleus_table
from ..service import create_nucleo, delete_nucleo, update_nucleo
from .serializers import (
    NucleosCreateSerializer,
    NucleosDetailSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses={200: NucleosListSerializer(many=True)},
        description="List all nucleos",
        tags=["Nucleo Management"],
    ),
    post=extend_schema(
        request=NucleosCreateSerializer,
        responses={201: NucleosListSerializer},
        description="Create a new nucleo",
        tags=["Nucleo Management"],
    ),
)
class NucleoListCreateView(RoleRequiredMixin, APIView):
    def get(self, request: Request):

        nuclei = get_nucleus_table()

        serializer = NucleosListSerializer(nuclei, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request: Request):
        serializer = NucleosCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nucleus = create_nucleo(
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
            image=serializer.validated_data.get("image"),
        )

        serializer = NucleosListSerializer(get_nucleus_by_id(nucleus.id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses={200: NucleosDetailSerializer},
        description="Get a nucleus by ID",
        tags=["Nucleo Management"],
    ),
    put=extend_schema(
        request=NucleosUpdateSerializer,
        responses={200: NucleosDetailSerializer},
        description="Update a nucleus",
        tags=["Nucleo Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a nucleus",
        tags=["Nucleo Management"],
    ),
)
class NucleoDetailView(RoleRequiredMixin, APIView):
    def get(self, request, nucleo_id):
        nucleus = get_nucleus_by_id(nucleo_id)

        serializer = NucleosDetailSerializer(nucleus)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, nucleo_id):
        serializer = NucleosUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nucleus = update_nucleo(
            nucleo_id=nucleo_id,
            name=serializer.validated_data.get("name"),
            abbreviation=serializer.validated_data.get("abbreviation"),
            image=serializer.validated_data.get("image"),
        )

        serializer = NucleosDetailSerializer(get_nucleus_by_id(nucleus.id))
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def delete(self, request, nucleo_id):
        delete_nucleo(nucleo_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", NucleoListCreateView.as_view(), name="nucleus-list"),
    path("<uuid:nucleo_id>/", NucleoDetailView.as_view(), name="nucleus-detail"),
]
