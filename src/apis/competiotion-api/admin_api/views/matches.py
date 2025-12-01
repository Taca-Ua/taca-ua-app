"""
Match management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import (
    MatchCommentSerializer,
    MatchCreateSerializer,
    MatchLineupSerializer,
    MatchListSerializer,
    MatchResultSerializer,
    MatchUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        responses=MatchListSerializer(many=True),
        description="List all matches",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=MatchCreateSerializer,
        responses=MatchListSerializer,
        description="Create a new match",
        tags=["Match Management"],
    ),
)
class MatchListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "tournament_id": 1,
                "team_home_id": 1,
                "team_away_id": 2,
                "location": "Campo 1",
                "start_time": "2025-02-10T15:00:00Z",
                "status": "scheduled",
                "home_score": None,
                "away_score": None,
            },
            {
                "id": 2,
                "tournament_id": 1,
                "team_home_id": 1,
                "team_away_id": 3,
                "location": "Campo 2",
                "start_time": "2025-02-15T16:00:00Z",
                "status": "finished",
                "home_score": 3,
                "away_score": 1,
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": 3,
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
            **serializer.validated_data,
        }
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=MatchUpdateSerializer,
        responses=MatchListSerializer,
        description="Update a match",
        tags=["Match Management"],
    ),
)
class MatchDetailView(APIView):
    def put(self, request, match_id):
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {
            "id": match_id,
            "tournament_id": 1,
            "team_home_id": serializer.validated_data.get("team_home_id", 1),
            "team_away_id": serializer.validated_data.get("team_away_id", 2),
            "location": serializer.validated_data.get("location", "Campo 1"),
            "start_time": serializer.validated_data.get(
                "start_time", "2025-02-10T15:00:00Z"
            ),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        }
        return Response(dummy_response)


@extend_schema(
    request=MatchResultSerializer,
    responses=MatchListSerializer,
    description="Register match result",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_result(request, match_id):
    serializer = MatchResultSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "id": match_id,
        "tournament_id": 1,
        "team_home_id": 1,
        "team_away_id": 2,
        "location": "Campo 1",
        "start_time": "2025-02-10T15:00:00Z",
        "status": "finished",
        **serializer.validated_data,
    }
    return Response(dummy_response)


@extend_schema(
    request=MatchLineupSerializer,
    responses={200: None},
    description="Assign players to match lineup",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_lineup(request, match_id):
    serializer = MatchLineupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "match_id": match_id,
        "team_id": serializer.validated_data.get("team_id"),
        "players": serializer.validated_data.get("players"),
        "message": "Lineup assigned successfully",
    }
    return Response(dummy_response)


@extend_schema(
    request=MatchCommentSerializer,
    responses={201: None},
    description="Add comments to match",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_comments(request, match_id):
    serializer = MatchCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    dummy_response = {
        "id": 1,
        "match_id": match_id,
        "message": serializer.validated_data.get("message"),
        "created_at": "2025-12-01T12:00:00Z",
        "author": "Admin User",
    }
    return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF",
    tags=["Match Management"],
)
@api_view(["GET"])
def match_sheet(request, match_id):
    return Response({"message": "PDF generation not implemented"})
