from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import DictField
from rest_framework.views import APIView
from shared.auth.decorators import (
    RoleRequiredMixin,
    require_auth,
    require_roles_class_method,
)
from shared.auth.utils import RolesEnum

from ..queries import get_tournament, get_tournament_format_details, list_tournaments
from ..service import (
    add_competitors_to_tournament,
    create_tournament,
    delete_tournament,
    remove_competitors_from_tournament,
    update_tournament,
    update_tournament_format,
)
from .filters import TournamentListQuerySerializer
from .renders import render_tournament_detail, render_tournaments
from .serializers import (
    TournamentAddCompetitorsSerializer,
    TournamentCreateSerializer,
    TournamentDetailSerializer,
    TournamentListSerializer,
    TournamentRemoveCompetitorsSerializer,
    TournamentUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List tournaments",
        description="Retrieve a list of tournaments with optional filtering.",
        parameters=[TournamentListQuerySerializer],
        responses={200: TournamentListSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create a tournament",
        description="Create a new tournament with the provided details.",
        request=TournamentCreateSerializer,
        responses={201: TournamentListSerializer},
    ),
)
class TournamentListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        serializer = TournamentListQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        tournaments = list_tournaments(
            status=serializer.validated_data.get("status"),
            modality_id=serializer.validated_data.get("modality_id"),
            season_id=serializer.validated_data.get("season_id"),
        )

        serializer = TournamentListSerializer(
            render_tournaments(tournaments).all(), many=True
        )
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request):
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tournament = create_tournament(
            name=serializer.validated_data["name"],
            modality_id=serializer.validated_data["modality_id"],
            start_date=serializer.validated_data.get("start_date"),
            season_id=serializer.validated_data.get("season_id"),
            scoring_format_id=serializer.validated_data.get("scoring_format_id"),
            format=serializer.validated_data.get("format"),
            format_data=serializer.validated_data.get("format_data"),
        )

        serializer = TournamentListSerializer(
            render_tournament_detail(tournament).first()
        )
        return Response(serializer.data, status=201)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve tournament details",
        description="Get detailed information about a specific tournament.",
        responses={200: TournamentDetailSerializer},
    ),
    put=extend_schema(
        summary="Update a tournament",
        description="Update the details of an existing tournament.",
        request=TournamentUpdateSerializer,
        responses={200: TournamentDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete a tournament",
        description="Remove a tournament from the system.",
        responses={204: None},
    ),
)
class TournamentDetailView(APIView):
    def get(self, request, tournament_id):
        tournament = get_tournament(tournament_id)

        serializer = TournamentDetailSerializer(
            render_tournament_detail(tournament).first()
        )
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, tournament_id):
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tournament = update_tournament(
            tournament_id=tournament_id,
            name=serializer.validated_data.get("name"),
            start_date=serializer.validated_data.get("start_date"),
            status=serializer.validated_data.get("status"),
        )

        serializer = TournamentDetailSerializer(
            render_tournament_detail(tournament).first()
        )
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def delete(self, request, tournament_id):
        delete_tournament(tournament_id)
        return Response(status=204)


@extend_schema(
    summary="Add competitor to tournament",
    description="Add a competitor (individual or team) to a tournament.",
    request=TournamentAddCompetitorsSerializer,
    responses={200: TournamentDetailSerializer},
)
@api_view(["PUT"])
@require_auth
def add_competitor_to_tournament(request, tournament_id):
    serializer = TournamentAddCompetitorsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    tournament = add_competitors_to_tournament(
        tournament_id=tournament_id,
        competitor_ids=serializer.validated_data["entity_ids"],
    )

    serializer = TournamentDetailSerializer(
        render_tournament_detail(tournament).first()
    )
    return Response(serializer.data)


@extend_schema(
    summary="Remove competitor from tournament",
    description="Remove a competitor (individual or team) from a tournament.",
    request=TournamentRemoveCompetitorsSerializer,
    responses={200: TournamentDetailSerializer},
)
@api_view(["PUT"])
@require_auth
def remove_competitor_from_tournament(request, tournament_id):
    serializer = TournamentRemoveCompetitorsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    tournament = remove_competitors_from_tournament(
        tournament_id=tournament_id,
        competitor_ids=serializer.validated_data["competitor_ids"],
    )

    serializer = TournamentDetailSerializer(
        render_tournament_detail(tournament).first()
    )
    return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve tournament format details",
        description="Get detailed information about a tournament's format and its current state.",
        responses={200: DictField},
    ),
    put=extend_schema(
        summary="Update tournament format",
        description="Update the format of an existing tournament.",
        request=DictField,
        responses={200: DictField},
    ),
)
class TournamentFormatDetailView(RoleRequiredMixin, APIView):
    def get(self, request, tournament_id):
        format_details = get_tournament_format_details(tournament_id)
        return Response(format_details, status=200)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def put(self, request, tournament_id):

        format_details = update_tournament_format(
            tournament_id=tournament_id,
            format_data=request.data,
        )

        return Response(format_details, status=200)


urlpatterns = [
    path("", TournamentListCreateView.as_view(), name="tournament-list-create"),
    path(
        "<uuid:tournament_id>/",
        TournamentDetailView.as_view(),
        name="tournament-detail",
    ),
    path(
        "<uuid:tournament_id>/add-competitors/",
        add_competitor_to_tournament,
        name="tournament-add-competitors",
    ),
    path(
        "<uuid:tournament_id>/remove-competitors/",
        remove_competitor_from_tournament,
        name="tournament-remove-competitors",
    ),
    path(
        "<uuid:tournament_id>/format/",
        TournamentFormatDetailView.as_view(),
        name="tournament-format-detail",
    ),
]
