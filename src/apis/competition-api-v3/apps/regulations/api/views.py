from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import require_roles_class_method
from shared.auth.utils import RolesEnum

from ..queries import get_all_regulations, get_regulation_by_id
from ..service import create_regulation, delete_regulation, update_regulation
from .filters import RegulationQueryListSerializer
from .renders import render_regulation, render_regulations
from .serializers import (
    RegulationCreateSerializer,
    RegulationDetailSerializer,
    RegulationListSerializer,
    RegulationUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List Regulations",
        description="Retrieve a list of all regulations.",
        responses={200: RegulationListSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create Regulation",
        description="Create a new regulation.",
        request=RegulationCreateSerializer,
        parameters=[RegulationQueryListSerializer],
        responses={201: RegulationListSerializer},
    ),
)
class RegulationListCreateView(APIView):
    def get(self, request: Request) -> Response:
        regulations = get_all_regulations()

        serializer = RegulationListSerializer(
            render_regulations(regulations).all(), many=True
        )
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request: Request) -> Response:
        req_serializer = RegulationCreateSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        params_serializer = RegulationQueryListSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)

        regulation = create_regulation(
            file=req_serializer.validated_data["file"],
            title=req_serializer.validated_data["title"],
            description=req_serializer.validated_data.get("description"),
            season_id=params_serializer.validated_data.get("season_id"),
        )
        return Response(
            RegulationListSerializer(regulation).data, status=status.HTTP_201_CREATED
        )


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Regulation",
        description="Retrieve a regulation by its ID.",
        responses={200: RegulationDetailSerializer},
    ),
    put=extend_schema(
        summary="Update Regulation",
        description="Update an existing regulation.",
        request=RegulationUpdateSerializer,
        responses={200: RegulationDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete Regulation",
        description="Delete a regulation by its ID.",
        responses={204: None},
    ),
)
class RegulationDetailView(APIView):
    def get(self, request: Request, regulation_id: str) -> Response:
        regulation = get_regulation_by_id(regulation_id)

        serializer = RegulationDetailSerializer(
            render_regulation(regulation).first(),
        )
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request: Request, regulation_id: str) -> Response:
        serializer = RegulationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        regulation = update_regulation(
            regulation_id=regulation_id,
            file=serializer.validated_data.get("file"),
            title=serializer.validated_data.get("title"),
            description=serializer.validated_data.get("description"),
        )
        return Response(RegulationDetailSerializer(regulation).data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def delete(self, request: Request, regulation_id: str) -> Response:
        delete_regulation(regulation_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", RegulationListCreateView.as_view(), name="regulation-list-create"),
    path(
        "<str:regulation_id>/", RegulationDetailView.as_view(), name="regulation-detail"
    ),
]
