"""
Team management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import TeamCreateSerializer, TeamListSerializer, TeamUpdateSerializer
from .auth import get_authenticated_user


@extend_schema_view(
    get=extend_schema(
        responses=TeamListSerializer(many=True),
        description="List teams for the authenticated nucleo (filtered by course_id)",
        tags=["Team Management"],
    ),
    post=extend_schema(
        request=TeamCreateSerializer,
        responses=TeamListSerializer,
        description="Create a new team for the authenticated nucleo",
        tags=["Team Management"],
    ),
)
class TeamListCreateView(APIView):
    def get(self, request):
        # Get authenticated user
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Mock database of all teams
        all_teams = [
            {
                "id": 1,
                "modality_id": 1,  # Futebol
                "course_id": 1,
                "name": "MECT Futebol A",
                "players": [1, 2, 3, 4, 5, 11, 12],  # 7 players for football
            },
            {
                "id": 2,
                "modality_id": 1,  # Futebol
                "course_id": 2,
                "name": "LEI Futebol A",
                "players": [6, 7, 8, 9, 10, 21],  # 6 players for football
            },
            {
                "id": 3,
                "modality_id": 2,  # Futsal
                "course_id": 1,
                "name": "MECT Futsal",
                "players": [1, 2, 13, 14, 15],  # 5 players for futsal
            },
            {
                "id": 4,
                "modality_id": 5,  # Andebol
                "course_id": 1,
                "name": "MECT Andebol",
                "players": [3, 4, 11, 12, 13, 14],  # 6 players for handball
            },
            {
                "id": 5,
                "modality_id": 1,  # Futebol
                "course_id": 3,
                "name": "LECI Futebol A",
                "players": [16, 17, 18, 19, 20],  # 5 players for football
            },
            {
                "id": 6,
                "modality_id": 2,  # Futsal
                "course_id": 2,
                "name": "LEI Futsal",
                "players": [6, 21, 22, 23],  # 4 players for futsal
            },
        ]

        # Check if 'all' query parameter is provided
        show_all = request.query_params.get("all", "false").lower() == "true"

        if show_all:
            # Return all teams (needed for match details with teams from other courses)
            return Response(all_teams)
        else:
            # Filter teams by user's course_id (default behavior)
            filtered_teams = [
                team for team in all_teams if team["course_id"] == user["course_id"]
            ]
            return Response(filtered_teams)

    def post(self, request):
        # Get authenticated user
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Auto-assign the team to the authenticated user's course
        dummy_response = {
            "id": 7,
            "course_id": user["course_id"],
            **serializer.validated_data,
        }
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema_view(
    put=extend_schema(
        request=TeamUpdateSerializer,
        responses=TeamListSerializer,
        description="Update a team",
        tags=["Team Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a team",
        tags=["Team Management"],
    ),
)
class TeamDetailView(APIView):
    def put(self, request, team_id):
        serializer = TeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_players = [1, 2, 3]
        players_add = serializer.validated_data.get("players_add", [])
        players_remove = serializer.validated_data.get("players_remove", [])
        updated_players = [
            p for p in current_players if p not in players_remove
        ] + players_add
        dummy_response = {
            "id": team_id,
            "modality_id": 1,
            "course_id": 1,
            "name": serializer.validated_data.get("name", f"Team {team_id}"),
            "players": updated_players,
        }
        return Response(dummy_response)

    def delete(self, request, team_id):
        return Response(status=status.HTTP_204_NO_CONTENT)
