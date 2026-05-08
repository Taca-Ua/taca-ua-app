"""
Team management views
"""

from admin_api.utils.decorators import RoleRequiredMixin
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    TeamCreateSerializer,
    TeamDetailSerializer,
    TeamListRequestSerializer,
    TeamListSerializer,
    TeamUpdateSerializer,
)
from .service import teams_service


@extend_schema_view(
    get=extend_schema(
        parameters=[TeamListRequestSerializer],
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
class TeamListCreateView(RoleRequiredMixin, APIView):
    def get(self, request: Request):
        # Serialize input data
        serializer = TeamListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # TODO: Pass remaining filters (e.g., course_id, tournament_id) to the modalities service client when supported
        teams = teams_service.list_teams(
            admin_id=str(request.user_id) if "nucleo_admin" in request.roles else None,
            modality_id=(
                str(serializer.validated_data["modality_id"])
                if "modality_id" in serializer.validated_data
                else None
            ),
            season_id=serializer.validated_data.get("season_id"),
        )

        # Serialize output data
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        # Serialize input data
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = teams_service.create_team(
            name=serializer.validated_data.get("name"),
            modality_id=str(serializer.validated_data["modality_id"]),
            course_id=str(serializer.validated_data["course_id"]),
            season_id=serializer.validated_data.get("season_id"),
        )

        # Serialize output data
        serializer = TeamListSerializer(team)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=TeamDetailSerializer,
        description="Get a team by ID",
        tags=["Team Management"],
    ),
    put=extend_schema(
        request=TeamUpdateSerializer,
        responses=TeamDetailSerializer,
        description="Update a team (name, add/remove players)",
        tags=["Team Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a team",
        tags=["Team Management"],
    ),
)
class TeamDetailView(RoleRequiredMixin, APIView):
    def get(self, request, team_id):
        team = teams_service.get_team(team_id)

        # Serialize output data
        serializer = TeamDetailSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, team_id):
        # Serialize input data
        serializer = TeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = teams_service.update_team(
            team_id,
            name=serializer.validated_data.get("name"),
            players_add=(
                [str(pid) for pid in serializer.validated_data["players_add"]]
                if "players_add" in serializer.validated_data
                else None
            ),
            players_remove=(
                [str(pid) for pid in serializer.validated_data["players_remove"]]
                if "players_remove" in serializer.validated_data
                else None
            ),
        )

        # Serialize output data
        serializer = TeamDetailSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, team_id):
        teams_service.delete_team(team_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", TeamListCreateView.as_view(), name="team-list"),
    path("<uuid:team_id>/", TeamDetailView.as_view(), name="team-detail"),
]
