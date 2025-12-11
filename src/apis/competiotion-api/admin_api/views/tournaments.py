"""
Tournament management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    TournamentCreateSerializer,
    TournamentListSerializer,
    TournamentUpdateSerializer,
)

# Mock database for tournaments
MOCK_TOURNAMENTS = {
    "1": {
        "id": 1,
        "modality_id": 1,
        "name": "Campeonato Futebol 25/26",
        "season_id": 1,
        "season_year": "25/26",
        "rules": "Formato eliminatória com 8 equipas",
        "status": "active",
        "start_date": "2025-02-01T10:00:00Z",
        "teams": [1, 2, 3, 4, 5, 6, 7, 8],
    },
    "2": {
        "id": 2,
        "modality_id": 2,
        "name": "Campeonato Futsal 25/26",
        "season_id": 1,
        "season_year": "25/26",
        "rules": "Todos contra todos",
        "status": "draft",
        "start_date": None,
        "teams": [],
    },
    "3": {
        "id": 3,
        "modality_id": 3,
        "name": "Taça Basquetebol 24/25",
        "season_id": 2,
        "season_year": "24/25",
        "rules": "Fase de grupos seguida de playoff",
        "status": "finished",
        "start_date": "2024-11-15T14:00:00Z",
        "teams": [10, 11, 12, 13],
    },
    "4": {
        "id": 4,
        "modality_id": 4,
        "name": "Liga Voleibol 25/26",
        "season_id": 1,
        "season_year": "25/26",
        "rules": "Sistema de liga com ida e volta",
        "status": "draft",
        "start_date": None,
        "teams": [14, 15],
    },
}

NEXT_TOURNAMENT_ID = 5


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
        tournaments_list = list(MOCK_TOURNAMENTS.values())
        return Response(tournaments_list)

    def post(self, request):
        """Create a new tournament"""
        global NEXT_TOURNAMENT_ID

        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_tournament = {
            "id": NEXT_TOURNAMENT_ID,
            "modality_id": serializer.validated_data["modality_id"],
            "name": serializer.validated_data["name"],
            "season_id": serializer.validated_data["season_id"],
            "season_year": serializer.validated_data.get("season_year", "25/26"),
            "rules": serializer.validated_data.get("rules", ""),
            "status": "draft",
            "start_date": serializer.validated_data.get("start_date"),
            "teams": serializer.validated_data.get("teams", []),
        }

        MOCK_TOURNAMENTS[NEXT_TOURNAMENT_ID] = new_tournament
        NEXT_TOURNAMENT_ID += 1

        return Response(new_tournament, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=TournamentListSerializer,
        description="Get tournament by ID",
        tags=["Tournament Management"],
    ),
    put=extend_schema(
        request=TournamentUpdateSerializer,
        responses=TournamentListSerializer,
        description="Update a tournament",
        tags=["Tournament Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a tournament",
        tags=["Tournament Management"],
    ),
)
class TournamentDetailView(APIView):
    def get(self, request, tournament_id):
        """Get tournament details by ID"""
        tournament = MOCK_TOURNAMENTS.get(tournament_id)
        if not tournament:
            return Response(
                {"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(tournament)

    def put(self, request, tournament_id):
        """Update a tournament"""
        tournament = MOCK_TOURNAMENTS.get(tournament_id)
        if not tournament:
            return Response(
                {"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if tournament is finished (locked)
        if tournament["status"] == "finished":
            return Response(
                {"error": "Cannot update a finished tournament"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update tournament fields
        if "name" in serializer.validated_data:
            tournament["name"] = serializer.validated_data["name"]
        if "rules" in serializer.validated_data:
            tournament["rules"] = serializer.validated_data["rules"]
        if "teams" in serializer.validated_data:
            tournament["teams"] = serializer.validated_data["teams"]
        if "start_date" in serializer.validated_data:
            tournament["start_date"] = serializer.validated_data["start_date"]

        return Response(tournament)

    def delete(self, request, tournament_id):
        """Delete a tournament"""
        if tournament_id not in MOCK_TOURNAMENTS:
            return Response(
                {"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND
            )

        del MOCK_TOURNAMENTS[tournament_id]
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=None,
    responses={200: TournamentListSerializer},
    description="Finish a tournament",
    tags=["Tournament Management"],
)
@api_view(["POST"])
def tournament_finish(request, tournament_id):
    """Mark a tournament as finished"""
    tournament = MOCK_TOURNAMENTS.get(tournament_id)
    if not tournament:
        return Response(
            {"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if tournament["status"] == "finished":
        return Response(
            {"error": "Tournament is already finished"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tournament["status"] = "finished"
    return Response(tournament)
