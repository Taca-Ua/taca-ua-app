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
from .auth import get_authenticated_user


@extend_schema_view(
    get=extend_schema(
        responses=MatchListSerializer(many=True),
        description="List matches involving the authenticated nucleo's teams (filtered by course_id)",
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
        # Get authenticated user
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Mock database of teams (to determine which matches belong to this nucleo)
        teams = [
            {"id": 1, "course_id": 1, "name": "MECT Futebol A", "modality_id": 1},
            {"id": 2, "course_id": 2, "name": "LEI Futebol A", "modality_id": 1},
            {"id": 3, "course_id": 1, "name": "MECT Futsal", "modality_id": 2},
            {"id": 4, "course_id": 1, "name": "MECT Andebol", "modality_id": 5},
            {"id": 5, "course_id": 3, "name": "LECI Futebol A", "modality_id": 1},
            {"id": 6, "course_id": 2, "name": "LEI Futsal", "modality_id": 2},
        ]

        # Mock database of all matches
        all_matches = [
            # Futebol matches
            {
                "id": 1,
                "tournament_id": 1,
                "team_home_id": 1,  # MECT Futebol A
                "team_away_id": 2,  # LEI Futebol A
                "location": "Campo 1 - Complexo Desportivo UA",
                "start_time": "2025-12-10T15:00:00Z",
                "status": "scheduled",
                "home_score": None,
                "away_score": None,
            },
            {
                "id": 2,
                "tournament_id": 1,
                "team_home_id": 1,  # MECT Futebol A
                "team_away_id": 5,  # LECI Futebol A
                "location": "Campo 2 - Complexo Desportivo UA",
                "start_time": "2025-12-05T16:00:00Z",
                "status": "finished",
                "home_score": 3,
                "away_score": 1,
            },
            # Futsal matches
            {
                "id": 3,
                "tournament_id": 2,
                "team_home_id": 3,  # MECT Futsal
                "team_away_id": 6,  # LEI Futsal
                "location": "Pavilhão A - UA",
                "start_time": "2025-12-12T18:00:00Z",
                "status": "scheduled",
                "home_score": None,
                "away_score": None,
            },
            {
                "id": 4,
                "tournament_id": 2,
                "team_home_id": 6,  # LEI Futsal
                "team_away_id": 3,  # MECT Futsal
                "start_time": "2025-12-01T17:30:00Z",
                "location": "Pavilhão B - UA",
                "status": "finished",
                "home_score": 2,
                "away_score": 2,
            },
            # Andebol match
            {
                "id": 5,
                "tournament_id": 3,
                "team_home_id": 4,  # MECT Andebol
                "team_away_id": 2,  # LEI Futebol A (cross-sport friendly match - unlikely but for variety)
                "location": "Campo 3 - Complexo Desportivo UA",
                "start_time": "2025-12-20T14:00:00Z",
                "status": "scheduled",
                "home_score": None,
                "away_score": None,
            },
            # More upcoming matches
            {
                "id": 6,
                "tournament_id": 1,
                "team_home_id": 2,  # LEI Futebol A
                "team_away_id": 5,  # LECI Futebol A
                "location": "Campo 1 - Complexo Desportivo UA",
                "start_time": "2025-12-18T16:00:00Z",
                "status": "scheduled",
                "home_score": None,
                "away_score": None,
            },
            {
                "id": 7,
                "tournament_id": 1,
                "team_home_id": 5,  # LECI Futebol A
                "team_away_id": 1,  # MECT Futebol A
                "location": "Campo 2 - Complexo Desportivo UA",
                "start_time": "2025-12-25T15:00:00Z",
                "status": "scheduled",
                "home_score": None,
                "away_score": None,
            },
        ]

        # If user is geral admin (role "geral"), return all matches
        # If user is nucleo admin, filter by their teams
        if user.get("role") == "geral":
            return Response(all_matches)

        # Get team IDs for this nucleo
        nucleo_team_ids = [
            team["id"] for team in teams if team["course_id"] == user["course_id"]
        ]

        # Filter matches where either home or away team belongs to this nucleo
        filtered_matches = [
            match
            for match in all_matches
            if match["team_home_id"] in nucleo_team_ids
            or match["team_away_id"] in nucleo_team_ids
        ]

        return Response(filtered_matches)

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
    get=extend_schema(
        responses=MatchListSerializer,
        description="Get a specific match by ID",
        tags=["Match Management"],
    ),
    put=extend_schema(
        request=MatchUpdateSerializer,
        responses=MatchListSerializer,
        description="Update a match",
        tags=["Match Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a match",
        tags=["Match Management"],
    ),
)
class MatchDetailView(APIView):
    # Mock database of all matches (same as in MatchListCreateView)
    MOCK_MATCHES = [
        {
            "id": 1,
            "tournament_id": 1,
            "team_home_id": 1,
            "team_away_id": 2,
            "location": "Campo 1 - Complexo Desportivo UA",
            "start_time": "2025-12-10T15:00:00Z",
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 2,
            "tournament_id": 1,
            "team_home_id": 1,
            "team_away_id": 5,
            "location": "Campo 2 - Complexo Desportivo UA",
            "start_time": "2025-12-05T16:00:00Z",
            "status": "finished",
            "home_score": 3,
            "away_score": 1,
        },
        {
            "id": 3,
            "tournament_id": 2,
            "team_home_id": 3,
            "team_away_id": 6,
            "location": "Pavilhão A - UA",
            "start_time": "2025-12-12T18:00:00Z",
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 4,
            "tournament_id": 2,
            "team_home_id": 6,
            "team_away_id": 3,
            "start_time": "2025-12-01T17:30:00Z",
            "location": "Pavilhão B - UA",
            "status": "finished",
            "home_score": 2,
            "away_score": 2,
        },
        {
            "id": 5,
            "tournament_id": 3,
            "team_home_id": 4,
            "team_away_id": 2,
            "location": "Campo 3 - Complexo Desportivo UA",
            "start_time": "2025-12-20T14:00:00Z",
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 6,
            "tournament_id": 1,
            "team_home_id": 2,
            "team_away_id": 5,
            "location": "Campo 1 - Complexo Desportivo UA",
            "start_time": "2025-12-18T16:00:00Z",
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 7,
            "tournament_id": 1,
            "team_home_id": 5,
            "team_away_id": 1,
            "location": "Campo 2 - Complexo Desportivo UA",
            "start_time": "2025-12-25T15:00:00Z",
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
    ]

    def get(self, request, match_id):
        # Find match by ID
        match = next((m for m in self.MOCK_MATCHES if str(m["id"]) == match_id), None)
        if not match:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(match)

    def put(self, request, match_id):
        # Find match by ID
        match = next((m for m in self.MOCK_MATCHES if m["id"] == match_id), None)
        if not match:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update match with provided fields
        updated_match = {**match}
        for field, value in serializer.validated_data.items():
            updated_match[field] = value

        return Response(updated_match)

    def delete(self, request, match_id):
        # Find match by ID
        match = next((m for m in self.MOCK_MATCHES if m["id"] == match_id), None)
        if not match:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # In a real implementation, we would delete from database
        # For now, just return success
        return Response(status=status.HTTP_204_NO_CONTENT)


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
