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
        dummy_data = [
            {
                "id": 1,
                "modality_id": 1,
                "name": "Campeonato Futebol 2025",
                "season_id": 1,
                "rules": "Formato eliminatória",
                "status": "active",
                "start_date": "2025-02-01T10:00:00Z",
                "teams": [1, 2, 3],
            },
            {
                "id": 2,
                "modality_id": 2,
                "name": "Campeonato Futsal 2025",
                "season_id": 1,
                "rules": "Todos contra todos",
                "status": "draft",
                "start_date": None,
                "teams": [],
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 3, "status": "draft", **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
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
    def put(self, request, tournament_id):
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": tournament_id,
            "modality_id": 1,
            "name": serializer.validated_data.get(
                "name", f"Tournament {tournament_id}"
            ),
            "season_id": 1,
            "rules": serializer.validated_data.get("rules", ""),
            "status": "active",
            "start_date": serializer.validated_data.get("start_date"),
            "teams": serializer.validated_data.get("teams", []),
        }
        return Response(dummy_response)

    def delete(self, request, tournament_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=None,
    responses={200: TournamentListSerializer},
    description="Finish a tournament",
    tags=["Tournament Management"],
)
@api_view(["POST"])
def tournament_finish(request, tournament_id):
    dummy_response = {
        "id": tournament_id,
        "modality_id": 1,
        "name": f"Tournament {tournament_id}",
        "season_id": 1,
        "rules": "Competition rules",
        "status": "finished",
        "start_date": "2025-02-01T10:00:00Z",
        "teams": [1, 2, 3, 4],
    }
    return Response(dummy_response)
