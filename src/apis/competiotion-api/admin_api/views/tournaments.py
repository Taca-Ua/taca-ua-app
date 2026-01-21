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

from ..serializers.tournaments import (
    TournamentCreateSerializer,
    TournamentDetailSerializer,
    TournamentFinishSerializer,
    TournamentListSerializer,
    TournamentUpdateSerializer,
)
from ..services.enricher_service import enricher_service
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
class TournamentListCreateView(APIView):
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

        try:
            # Call microservice
            tournament = tournaments_service_client.create_tournament(
                modality_id=serializer.validated_data["modality_id"],
                name=serializer.validated_data["name"],
                created_by="00000000-0000-0000-0000-000000000000",  # Placeholder
                start_date=(
                    serializer.validated_data.get("start_date").isoformat()
                    if serializer.validated_data.get("start_date")
                    else datetime.now().isoformat()
                ),
                teams_ids=serializer.validated_data.get("teams_ids", []),
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
class TournamentDetailView(APIView):
    def get(self, request, tournament_id):
        """Get tournament details by ID"""
        try:
            tournament = tournaments_service_client.get_tournament(tournament_id)

            # Enrich tournament info
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        enricher_service.complete_tournament_info(tournament)
        print("Tournament details:", tournament.__dict__.get("competitors", None))
        serializer = TournamentDetailSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, tournament_id):
        """Update a tournament"""
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
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
                competitors_add=serializer.validated_data.get("competitors_add"),
                competitors_remove=serializer.validated_data.get("competitors_remove"),
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
def tournament_finish(request, tournament_id):
    """Mark a tournament as finished"""
    serializer = TournamentFinishSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        # Prepare ranking entries
        ranking_entries = [
            {"team_id": str(entry["team_id"]), "position": entry["position"]}
            for entry in serializer.validated_data["ranking_entries"]
        ]

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
]
