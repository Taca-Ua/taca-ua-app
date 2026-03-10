"""
Tournament management views - Updated to use tournaments-service microservice
"""

from datetime import datetime

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators import RoleRequiredMixin, require_auth
from ..serializers.tournaments import (
    TournamentCompetitorsDeleteSerializer,
    TournamentCompetitorSerializer,
    TournamentCreateSerializer,
    TournamentDetailSerializer,
    TournamentFinishSerializer,
    TournamentListSerializer,
    TournamentUpdateSerializer,
)
from ..services.enricher_service import enricher_service
from ..services.modalities_service import modalities_service_client
from ..services.tournaments_service import tournaments_service_client


@extend_schema_view(
    get=extend_schema(
        responses=TournamentListSerializer(many=True),
        description="List all tournaments",
        tags=["Tournament Management"],
    ),
    post=extend_schema(
        request=TournamentCreateSerializer,
        responses=TournamentListSerializer,
        description="Create a new tournament",
        tags=["Tournament Management"],
    ),
)
class TournamentListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        """List all tournaments"""
        tournaments = tournaments_service_client.list_tournaments()

        # Enrich tournament info
        enricher_service.add_modality_to_tournaments(tournaments)

        serializer = TournamentListSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new tournament"""
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            # Determine modality type (playoff vs regular) to validate modality_id and set correct one for tournament creation
            scoring_format_id = None
            if data["is_playoff"]:
                playoff_modality_type = (
                    modalities_service_client.get_playoff_modality_type()
                )
                if not playoff_modality_type:
                    return Response(
                        {
                            "detail": "Playoff modality type not found. Cannot create playoff tournament."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                scoring_format_id = playoff_modality_type.id
            else:
                modality = modalities_service_client.get_modality(data["modality_id"])
                scoring_format_id = modality.modality_type.id

            # Create tournament
            tournament = tournaments_service_client.create_tournament(
                modality_id=serializer.validated_data["modality_id"],
                name=serializer.validated_data["name"],
                start_date=(
                    serializer.validated_data.get("start_date").isoformat()
                    if serializer.validated_data.get("start_date")
                    else datetime.now().isoformat()
                ),
                scoring_format_id=scoring_format_id,
            )

            # Enrich tournament info
            enricher_service.complete_tournament_info(tournament)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = TournamentListSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=TournamentDetailSerializer,
        description="Get tournament by ID",
        tags=["Tournament Management"],
    ),
    put=extend_schema(
        request=TournamentUpdateSerializer,
        responses=TournamentDetailSerializer,
        description="Update a tournament",
        tags=["Tournament Management"],
    ),
    delete=extend_schema(
        description="Delete a tournament",
        tags=["Tournament Management"],
    ),
)
class TournamentDetailView(RoleRequiredMixin, APIView):
    def get(self, request, tournament_id):
        """Get tournament details by ID"""
        try:
            tournament = tournaments_service_client.get_tournament(tournament_id)

            # Enrich tournament info
            enricher_service.complete_tournament_info(tournament)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = TournamentDetailSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, tournament_id):
        """Update a tournament"""
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            scoring_format_id = None
            if serializer.validated_data.get("is_playoff"):
                scoring_format_id = (
                    modalities_service_client.get_playoff_modality_type().id
                )
            elif serializer.validated_data.get("is_playoff") is False:
                if serializer.validated_data.get("modality_id"):
                    scoring_format_id = modalities_service_client.get_modality(
                        serializer.validated_data["modality_id"]
                    ).modality_type.id
                else:
                    # If modality_id is not being updated, we need to fetch the tournament's current modality to determine if it's playoff or not
                    current_tournament = tournaments_service_client.get_tournament(
                        tournament_id
                    )
                    scoring_format_id = modalities_service_client.get_modality(
                        current_tournament.modality_id
                    ).modality_type.id

            # Call microservice
            tournament = tournaments_service_client.update_tournament(
                tournament_id=tournament_id,
                name=serializer.validated_data.get("name"),
                start_date=(
                    serializer.validated_data.get("start_date").isoformat()
                    if serializer.validated_data.get("start_date")
                    else None
                ),
                status=serializer.validated_data.get("status"),
                scoring_format_id=scoring_format_id,
            )

            # Enrich tournament info
            enricher_service.complete_tournament_info(tournament)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = TournamentDetailSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, tournament_id):
        """Delete a tournament"""
        try:
            tournaments_service_client.delete_tournament(tournament_id)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=TournamentFinishSerializer,
    responses={200: TournamentDetailSerializer},
    description="Finish a tournament",
    tags=["Tournament Management"],
)
@api_view(["POST"])
@require_auth
def tournament_finish(request, tournament_id):
    """Mark a tournament as finished"""
    serializer = TournamentFinishSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        # Prepare ranking entries - extract competitor_id based on type
        ranking_entries = []
        for entry in serializer.validated_data["ranking_entries"]:
            if entry["competitor_type"] == "team":
                competitor_id = entry["team_id"]
            else:  # athlete
                competitor_id = entry["athlete_id"]

            ranking_entries.append(
                {"competitor_id": str(competitor_id), "position": entry["position"]}
            )

        # Call microservice
        tournament = tournaments_service_client.finish_tournament(
            tournament_id=tournament_id,
            ranking_entries=ranking_entries,
            finished_by="00000000-0000-0000-0000-000000000000",  # Placeholder
        )

        # Enrich tournament info
        enricher_service.complete_tournament_info(tournament)
    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    serializer = TournamentDetailSerializer(tournament)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=TournamentCompetitorSerializer(many=True),
    responses={200: TournamentDetailSerializer},
    description="Add competitors to a tournament",
    tags=["Tournament Management"],
)
@api_view(["PUT"])
@require_auth
def tournament_add_competitors(request, tournament_id):
    """Add competitors to a tournament"""
    serializer = TournamentCompetitorSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)

    try:
        # Call microservice
        tournament = tournaments_service_client.add_competitors(
            tournament_id=tournament_id,
            competitors_data=serializer.validated_data,
        )

        # Enrich tournament info
        enricher_service.complete_tournament_info(tournament)
    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    serializer = TournamentDetailSerializer(tournament)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=TournamentCompetitorsDeleteSerializer,
    responses={200: TournamentDetailSerializer},
    description="Remove competitors from a tournament",
    tags=["Tournament Management"],
)
@api_view(["PUT"])
@require_auth
def tournament_remove_competitors(request, tournament_id):
    """Remove competitors from a tournament"""
    serializer = TournamentCompetitorsDeleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        competitors_ids = serializer.validated_data["competitors_ids"]

        # Call microservice
        tournament = tournaments_service_client.remove_competitors(
            tournament_id=tournament_id,
            competitors_ids=competitors_ids,
        )

        # Enrich tournament info
        enricher_service.complete_tournament_info(tournament)
    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    serializer = TournamentDetailSerializer(tournament)
    return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("", TournamentListCreateView.as_view(), name="tournament-list"),
    path(
        "<uuid:tournament_id>/",
        TournamentDetailView.as_view(),
        name="tournament-detail",
    ),
    path(
        "<uuid:tournament_id>/finish/",
        tournament_finish,
        name="tournament-finish",
    ),
    path(
        "<uuid:tournament_id>/competitors/add/",
        tournament_add_competitors,
        name="tournament-add-competitors",
    ),
    path(
        "<uuid:tournament_id>/competitors/remove/",
        tournament_remove_competitors,
        name="tournament-remove-competitors",
    ),
]
