from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin, require_auth

from ..selectors import get_team_by_id, get_teams_table
from ..service import (
    add_athletes_to_team,
    create_team,
    delete_team,
    remove_athletes_from_team,
    update_team,
)
from .filters import TeamListRequestSerializer
from .serializers import (
    TeamAthleteUpdateSerializer,
    TeamCreateSerializer,
    TeamDetailSerializer,
    TeamListSerializer,
    TeamUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(
        summary="List Teams",
        description="Retrieve a list of teams with optional filtering by season, modality, or course.",
        tags=["Teams"],
        parameters=[TeamListRequestSerializer],
        responses={200: TeamListSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Create Team",
        description="Create a new team with the specified name, modality, course, and season.",
        tags=["Teams"],
        request=TeamCreateSerializer,
        responses={201: TeamListSerializer},
    ),
)
class TeamListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        serializer = TeamListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        teams = get_teams_table(
            season_id=serializer.validated_data.get("season_id"),
            modality_id=serializer.validated_data.get("modality_id"),
            course_id=serializer.validated_data.get("course_id"),
        )

        serialized = TeamListSerializer(teams, many=True)
        return Response(serialized.data)

    def post(self, request):
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = create_team(
            name=serializer.validated_data.get("name"),
            modality_id=serializer.validated_data["modality_id"],
            course_id=serializer.validated_data["course_id"],
            season_id=serializer.validated_data.get("season_id"),
        )

        serialized_team = TeamListSerializer(get_team_by_id(team.id))
        return Response(serialized_team.data, status=201)


@extend_schema_view(
    get=extend_schema(
        summary="Get Team Details",
        description="Retrieve detailed information about a specific team, including its players and season.",
        tags=["Teams"],
        responses={200: TeamDetailSerializer},
    ),
    put=extend_schema(
        summary="Update Team",
        description="Update the team's name, modality, course, season, or player roster.",
        tags=["Teams"],
        request=TeamUpdateSerializer,
        responses={200: TeamDetailSerializer},
    ),
    delete=extend_schema(
        summary="Delete Team",
        description="Delete a specific team by its ID.",
        tags=["Teams"],
        responses={204: None},
    ),
)
class TeamDetailView(RoleRequiredMixin, APIView):
    def get(self, request, team_id):
        team = get_team_by_id(team_id)

        serialized_team = TeamDetailSerializer(team)
        return Response(serialized_team.data, status=200)

    def put(self, request, team_id):
        serializer = TeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = update_team(
            team_id=team_id,
            name=serializer.validated_data.get("name"),
        )

        serialized_team = TeamDetailSerializer(team)
        return Response(serialized_team.data, status=200)

    def delete(self, request, team_id):
        delete_team(team_id)
        return Response(status=204)


@extend_schema(
    summary="Add Athlete to Team",
    description="Add an athlete to a team by providing the team ID and athlete ID.",
    tags=["Teams"],
    request=TeamAthleteUpdateSerializer,
    responses={200: TeamDetailSerializer},
)
@api_view(["PUT"])
@require_auth
def add_athlete(request, team_id):
    serializer = TeamAthleteUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    team = add_athletes_to_team(
        team_id=team_id,
        athlete_ids=serializer.validated_data["athlete_ids"],
    )

    serialized_team = TeamDetailSerializer(get_team_by_id(team.id))
    return Response(serialized_team.data, status=200)


@extend_schema(
    summary="Remove Athlete from Team",
    description="Remove an athlete from a team by providing the team ID and athlete ID.",
    tags=["Teams"],
    request=TeamAthleteUpdateSerializer,
    responses={200: TeamDetailSerializer},
)
@api_view(["PUT"])
@require_auth
def remove_athlete(request, team_id):
    serializer = TeamAthleteUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    team = remove_athletes_from_team(
        team_id=team_id,
        athlete_ids=serializer.validated_data["athlete_ids"],
    )

    serialized_team = TeamDetailSerializer(get_team_by_id(team.id))
    return Response(serialized_team.data, status=200)


urlpatterns = [
    path("", TeamListCreateView.as_view(), name="team-list-create"),
    path("<uuid:team_id>/", TeamDetailView.as_view(), name="team-detail"),
    path("<uuid:team_id>/add-athletes/", add_athlete, name="add-athlete"),
    path("<uuid:team_id>/remove-athletes/", remove_athlete, name="remove-athlete"),
]
