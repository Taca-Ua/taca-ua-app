"""
Team management views
"""

from datetime import datetime, timezone

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Course, Modality, Team
from ..serializers import TeamCreateSerializer, TeamListSerializer, TeamUpdateSerializer


@extend_schema_view(
    get=extend_schema(
        responses=TeamListSerializer(many=True),
        description="List teams with optional filters (modality_id, course_id, tournament_id)",
        tags=["Team Management"],
    ),
    post=extend_schema(
        request=TeamCreateSerializer,
        responses=TeamListSerializer,
        description="Create a new team for a modality and course",
        tags=["Team Management"],
    ),
)
class TeamListCreateView(APIView):
    def get(self, request: Request):
        teams = Team.objects.all()

        return Response(
            [
                {
                    "id": team.id,
                    "modality_name": team.modality.name,
                    "course_name": team.course.name,
                    "name": team.name,
                }
                for team in teams
            ]
        )

    def post(self, request: Request):
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = Team.objects.create(
            name=serializer.validated_data.get("name"),
            modality_id=serializer.validated_data["modality_id"],
            course_id=serializer.validated_data["course_id"],
            created_by="00000000-0000-0000-0000-000000000000",
            created_at=datetime.now(timezone.utc),
        )

        return Response(
            {
                "id": team.id,
                "modality_name": team.modality.name,
                "course_name": team.course.name,
                "name": team.name,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        responses=TeamListSerializer,
        description="Get a team by ID",
        tags=["Team Management"],
    ),
    put=extend_schema(
        request=TeamUpdateSerializer,
        responses=TeamListSerializer,
        description="Update a team (name, add/remove players)",
        tags=["Team Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a team",
        tags=["Team Management"],
    ),
)
class TeamDetailView(APIView):
    def get(self, request, team_id):

        team = Team.objects.get(id=team_id)

        return Response(
            {
                "id": team.id,
                "modality_name": team.modality.name,
                "course_name": team.course.name,
                "name": team.name,
                "players": [player.to_json() for player in team.players.all()],
            }
        )

    def put(self, request, team_id):
        serializer = TeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = Team.objects.get(id=team_id)

        if "name" in serializer.validated_data:
            team.name = serializer.validated_data["name"]
        if "modality_id" in serializer.validated_data:
            modality = Modality.objects.get(id=serializer.validated_data["modality_id"])
            team.modality = modality
        if "course_id" in serializer.validated_data:
            course = Course.objects.get(id=serializer.validated_data["course_id"])
            team.course = course
        if "players_add" in serializer.validated_data:
            for player_id in serializer.validated_data["players_add"]:
                team.players.add(player_id)
        if "players_remove" in serializer.validated_data:
            for player_id in serializer.validated_data["players_remove"]:
                team.players.remove(player_id)
        team.save()

        return Response(
            {
                "id": team.id,
                "modality_name": team.modality.name,
                "course_name": team.course.name,
                "name": team.name,
                "players": [player.to_json() for player in team.players.all()],
            }
        )

    def delete(self, request, team_id):

        team = Team.objects.get(id=team_id)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
