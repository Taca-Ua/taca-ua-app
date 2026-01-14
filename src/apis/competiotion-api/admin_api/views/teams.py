"""
Team management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.teams import (
    TeamCreateSerializer,
    TeamDetailSerializer,
    TeamListRequestSerializer,
    TeamListSerializer,
    TeamUpdateSerializer,
)
from ..services.modalities_service import modalities_service_client


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
class TeamListCreateView(APIView):
    def get(self, request: Request):
        # Serialize input data
        serializer = TeamListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # TODO: Pass filters to the modalities service client
        teams = modalities_service_client.list_teams()

        # Serialize output data
        serializer = TeamListSerializer(data=teams, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        # Serialize input data
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = modalities_service_client.create_team(
            {
                "name": serializer.validated_data.get("name"),
                "modality_id": str(serializer.validated_data["modality_id"]),
                "course_id": str(serializer.validated_data["course_id"]),
            }
        )

        # Serialize output data
        serializer = TeamListSerializer(data=team)
        serializer.is_valid(raise_exception=True)
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
class TeamDetailView(APIView):
    def get(self, request, team_id):
        team = modalities_service_client.get_team(team_id)

        # Serialize output data
        serializer = TeamDetailSerializer(data=team)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, team_id):
        # Serialize input data
        serializer = TeamUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_data = {}
        if "name" in serializer.validated_data:
            update_data["name"] = serializer.validated_data["name"]
        if "modality_id" in serializer.validated_data:
            update_data["modality_id"] = str(serializer.validated_data["modality_id"])
        if "course_id" in serializer.validated_data:
            update_data["course_id"] = str(serializer.validated_data["course_id"])
        if "players_add" in serializer.validated_data:
            update_data["players_add"] = [
                str(pid) for pid in serializer.validated_data["players_add"]
            ]
        if "players_remove" in serializer.validated_data:
            update_data["players_remove"] = [
                str(pid) for pid in serializer.validated_data["players_remove"]
            ]

        team = modalities_service_client.update_team(team_id, update_data)

        # Serialize output data
        serializer = TeamDetailSerializer(data=team)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, team_id):
        modalities_service_client.delete_team(team_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", TeamListCreateView.as_view(), name="team-list"),
    path("<uuid:team_id>/", TeamDetailView.as_view(), name="team-detail"),
]
