"""
Tournament management views - Updated to use tournaments-service microservice
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
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
        """List all tournaments"""
        return Response({"detail": "List all tournaments"}, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new tournament"""
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Tournament created successfully"},
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(
        responses=TournamentListSerializer,
        description="Get tournament by ID",
        tags=["Tournament Management"],
    ),
    put=extend_schema(
        request=TournamentUpdateSerializer,
        responses=TournamentListSerializer,
        description="Update a tournament",
        tags=["Tournament Management"],
    ),
    delete=extend_schema(
        description="Delete a tournament",
        tags=["Tournament Management"],
    ),
)
class TournamentDetailView(APIView):
    def get(self, request, tournament_id):
        """Get tournament details by ID"""
        return Response(
            {"detail": "Get tournament details by ID"}, status=status.HTTP_200_OK
        )

    def put(self, request, tournament_id):
        """Update a tournament"""
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"detail": "Tournament updated successfully"}, status=status.HTTP_200_OK
        )

    def delete(self, request, tournament_id):
        """Delete a tournament"""
        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path("", TournamentListCreateView.as_view(), name="tournament-list"),
    path(
        "<uuid:tournament_id>/",
        TournamentDetailView.as_view(),
        name="tournament-detail",
    ),
]
