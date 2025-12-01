"""
Team management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import TeamCreateSerializer, TeamListSerializer, TeamUpdateSerializer


@extend_schema_view(
    get=extend_schema(
        responses=TeamListSerializer(many=True),
        description="List all teams",
        tags=["Team Management"],
    ),
    post=extend_schema(
        request=TeamCreateSerializer,
        responses=TeamListSerializer,
        description="Create a new team",
        tags=["Team Management"],
    ),
)
class TeamListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {
                "id": 1,
                "modality_id": 1,
                "course_id": 1,
                "name": "MECT A",
                "players": [1, 2, 3, 4, 5],
            },
            {
                "id": 2,
                "modality_id": 1,
                "course_id": 2,
                "name": "LEI A",
                "players": [6, 7, 8, 9, 10],
            },
            {
                "id": 3,
                "modality_id": 2,
                "course_id": 1,
                "name": "MECT Futsal",
                "players": [1, 2, 11, 12],
            },
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, "course_id": 1, **serializer.validated_data}
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
