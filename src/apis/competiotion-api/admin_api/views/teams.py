"""
Team management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import TeamCreateSerializer, TeamListSerializer, TeamUpdateSerializer
from ..services.modalities_service import ModalitiesService


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
        service = ModalitiesService()

        # Extract filters from query parameters
        modality_id = request.query_params.get("modality_id")
        course_id = request.query_params.get("course_id")
        tournament_id = request.query_params.get("tournament_id")
        limit = request.query_params.get("limit", 50)
        offset = request.query_params.get("offset", 0)

        teams_data = service.list_teams(
            modality_id=modality_id,
            course_id=course_id,
            tournament_id=tournament_id,
            limit=int(limit),
            offset=int(offset),
        )

        return Response(teams_data["teams"])

    def post(self, request: Request):
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ModalitiesService()

        team = service.create_team(
            modality_id=str(serializer.validated_data["modality_id"]),
            course_id=str(serializer.validated_data["course_id"]),
            created_by=(
                str(request.user.id)
                if request.user.id
                else "00000000-0000-0000-0000-000000000000"
            ),
            name=serializer.validated_data.get("name"),
            players=[str(p) for p in serializer.validated_data.get("players", [])],
        )

        return Response(team, status=status.HTTP_201_CREATED)


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
        service = ModalitiesService()
        team = service.get_team(team_id)
        return Response(team)

    def put(self, request, team_id):
        serializer = TeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ModalitiesService()

        players_add = serializer.validated_data.get("players_add")
        players_remove = serializer.validated_data.get("players_remove")

        team = service.update_team(
            team_id=team_id,
            updated_by=(
                str(request.user.id)
                if request.user.id
                else "00000000-0000-0000-0000-000000000000"
            ),
            name=serializer.validated_data.get("name"),
            players_add=[str(p) for p in players_add] if players_add else None,
            players_remove=[str(p) for p in players_remove] if players_remove else None,
        )

        return Response(team)

    def delete(self, request, team_id):
        service = ModalitiesService()
        service.delete_team(team_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
