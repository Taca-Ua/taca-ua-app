from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import (
    RoleRequiredMixin,
    require_roles,
    require_roles_class_method,
)
from shared.auth.utils import RolesEnum

from ..selectors import get_nucleus_by_id, get_nucleus_table
from ..service import (
    add_nucleus_to_season,
    create_nucleo,
    remove_nucleus_from_season,
    update_nucleo,
)
from .filters import NucleusSeasonContextSerializer
from .serializers import (
    NucleosCreateSerializer,
    NucleosDetailSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        parameters=[NucleusSeasonContextSerializer],
        responses={200: NucleosListSerializer(many=True)},
        description="List all nucleos",
        tags=["Nucleo Management"],
    ),
    post=extend_schema(
        parameters=[NucleusSeasonContextSerializer],
        request=NucleosCreateSerializer,
        responses={201: NucleosListSerializer},
        description="Create a new nucleo",
        tags=["Nucleo Management"],
    ),
)
class NucleoListCreateView(RoleRequiredMixin, APIView):
    def get(self, request: Request):
        serializer = NucleusSeasonContextSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        nuclei = get_nucleus_table(
            context_season_id=serializer.validated_data.get("season_id")
        )

        serializer = NucleosListSerializer(nuclei, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request: Request):
        serializer = NucleosCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        params_serializer = NucleusSeasonContextSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)

        nucleus = create_nucleo(
            name=serializer.validated_data["name"],
            abbreviation=serializer.validated_data["abbreviation"],
            image=serializer.validated_data.get("image"),
        )

        serializer = NucleosListSerializer(
            get_nucleus_by_id(
                nucleus.id,
                context_season_id=params_serializer.validated_data.get("season_id"),
            )
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        parameters=[NucleusSeasonContextSerializer],
        responses={200: NucleosDetailSerializer},
        description="Get a nucleus by ID",
        tags=["Nucleo Management"],
    ),
    put=extend_schema(
        parameters=[NucleusSeasonContextSerializer],
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
        params_serializer = NucleusSeasonContextSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)

        nucleus = get_nucleus_by_id(
            nucleo_id,
            context_season_id=params_serializer.validated_data.get("season_id"),
        )

        serializer = NucleosDetailSerializer(nucleus)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, nucleo_id):
        serializer = NucleosUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        params_serializer = NucleusSeasonContextSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)

        nucleus = update_nucleo(
            nucleo_id=nucleo_id,
            name=serializer.validated_data.get("name"),
            abbreviation=serializer.validated_data.get("abbreviation"),
            image=serializer.validated_data.get("image"),
        )

        serializer = NucleosDetailSerializer(
            get_nucleus_by_id(
                nucleus.id,
                context_season_id=params_serializer.validated_data.get("season_id"),
            )
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Add Nucleus to Season",
    description="Adds a nucleus to a specific season.",
    tags=["Nucleo Management"],
    responses={200: NucleosListSerializer},
    parameters=[NucleusSeasonContextSerializer],
)
@api_view(["PUT"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def add_nucleus_to_season_view(request: Request, nucleus_id: str, season_id: int):
    params_serializer = NucleusSeasonContextSerializer(data=request.query_params)
    params_serializer.is_valid(raise_exception=True)

    nucleus = add_nucleus_to_season(nucleus_id, season_id)

    serializer = NucleosListSerializer(
        get_nucleus_by_id(
            nucleus.id,
            context_season_id=params_serializer.validated_data.get("season_id"),
        )
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Remove Nucleus from Season",
    description="Removes a nucleus from a specific season.",
    tags=["Nucleo Management"],
    responses={200: NucleosListSerializer},
    parameters=[NucleusSeasonContextSerializer],
)
@api_view(["PUT"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def remove_nucleus_from_season_view(request: Request, nucleus_id: str, season_id: int):
    params_serializer = NucleusSeasonContextSerializer(data=request.query_params)
    params_serializer.is_valid(raise_exception=True)

    nucleus = remove_nucleus_from_season(nucleus_id, season_id)

    serializer = NucleosListSerializer(
        get_nucleus_by_id(
            nucleus.id,
            context_season_id=params_serializer.validated_data.get("season_id"),
        )
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("", NucleoListCreateView.as_view(), name="nucleus-list"),
    path("<uuid:nucleo_id>/", NucleoDetailView.as_view(), name="nucleus-detail"),
    path(
        "<uuid:nucleus_id>/add_to_season/<int:season_id>/",
        add_nucleus_to_season_view,
        name="add-nucleus-to-season",
    ),
    path(
        "<uuid:nucleus_id>/remove_from_season/<int:season_id>/",
        remove_nucleus_from_season_view,
        name="remove-nucleus-from-season",
    ),
]
