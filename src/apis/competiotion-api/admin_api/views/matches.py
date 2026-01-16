"""
Match management views
"""

from uuid import UUID

import structlog
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers.matches import (
    MatchCommentRequestSerializer,
    MatchCreateSerializer,
    MatchLineupRequestSerializer,
    MatchListSerializer,
    MatchResultRequestSerializer,
    MatchUpdateSerializer,
)
from ..services.enricher_service import enricher_service
from ..services.matches_service import matches_service_client

logger = structlog.get_logger(__name__)


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
        # TODO: Filter by course_id when available
        result = matches_service_client.list_matches()
        matches = result.get("matches", [])

        # Populate participant details
        enricher_service.complete_matches_info(matches)

        serializer = MatchListSerializer(data=matches, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Prepare participants from team IDs
        participants = []
        if serializer.validated_data.get("team_home_id"):
            participants.append(
                {
                    "participant_type": "team",
                    "team_id": str(serializer.validated_data["team_home_id"]),
                }
            )
        if serializer.validated_data.get("team_away_id"):
            participants.append(
                {
                    "participant_type": "team",
                    "team_id": str(serializer.validated_data["team_away_id"]),
                }
            )

        # Create the match via service
        try:
            match = matches_service_client.create_match(
                tournament_id=serializer.validated_data.get("tournament_id"),
                location=serializer.validated_data["location"],
                start_time=serializer.validated_data["start_time"].isoformat(),
                created_by=UUID(
                    "00000000-0000-0000-0000-000000000000"
                ),  # TODO: Get from auth
                participants=participants,
            )

            # Populate participant details
            enricher_service.complete_matches_info([match])
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = MatchListSerializer(data=match)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
    def get(self, request, match_id):
        try:
            match = matches_service_client.get_match(match_id=match_id)

            # Populate participant details
            enricher_service.complete_matches_info([match])
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = MatchListSerializer(data=match)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, match_id):
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_data = {}

        if "location" in serializer.validated_data:
            update_data["location"] = serializer.validated_data["location"]
        if "start_time" in serializer.validated_data:
            update_data["start_time"] = serializer.validated_data[
                "start_time"
            ].isoformat()
        if "status" in serializer.validated_data:
            update_data["status"] = serializer.validated_data["status"]

        # Handle scores - need to update participants instead
        if (
            "home_score" in serializer.validated_data
            or "away_score" in serializer.validated_data
        ):
            # Validate both scores are provided
            if not all(
                field in serializer.validated_data
                for field in ("home_score", "away_score")
            ):
                raise serializers.ValidationError(
                    "Both home_score and away_score must be provided together."
                )

            # Get match to find participants
            try:
                match = matches_service_client.get_match(match_id=match_id)
                participants = match.get("participants", [])

                # Build participant results
                participant_results = []
                for idx, participant in enumerate(participants):
                    score = (
                        serializer.validated_data["home_score"]
                        if idx == 0
                        else serializer.validated_data["away_score"]
                    )
                    participant_results.append(
                        {
                            "participant_id": participant["id"],
                            "score": score,
                        }
                    )

                # Update results via service
                match = matches_service_client.update_match_results(
                    match_id=match_id,
                    participant_results=participant_results,
                    status=update_data.get("status", "finished"),
                )
                return Response(match, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(
                    {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Update match details only
        try:
            match = matches_service_client.update_match(
                match_id=match_id, **update_data
            )

            # Populate participant details
            enricher_service.complete_matches_info([match])

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = MatchListSerializer(data=match)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, match_id):
        try:
            matches_service_client.delete_match(match_id=match_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    request=MatchResultRequestSerializer,
    responses=MatchListSerializer,
    description="Register match result",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_result(request, match_id):
    serializer = MatchResultRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        # Get match to find participants
        match = matches_service_client.get_match(match_id=match_id)
        participants = match.get("participants", [])

        if len(participants) < 2:
            return Response(
                {"detail": "Match must have at least 2 participants."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build participant results (assuming first is home, second is away)
        participant_results = [
            {
                "participant_id": participants[0]["id"],
                "score": serializer.validated_data["home_score"],
            },
            {
                "participant_id": participants[1]["id"],
                "score": serializer.validated_data["away_score"],
            },
        ]

        # Update results and finish match
        updated_match = matches_service_client.update_match_results(
            match_id=match_id,
            participant_results=participant_results,
            status="finished",
        )

        # Populate participant details
        enricher_service.complete_matches_info([updated_match])

    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    serializer = MatchListSerializer(data=updated_match)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=MatchLineupRequestSerializer,
    responses={200: None},
    description="Assign players to match lineup",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_lineup(request, match_id):
    serializer = MatchLineupRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Convert serializer data to service format
    players = [
        {
            "player_id": str(player_data["player_id"]),
            "jersey_number": player_data["jersey_number"],
            "is_starter": player_data["is_starter"],
        }
        for player_data in serializer.validated_data["players"]
    ]

    try:
        result = matches_service_client.assign_lineup(
            match_id=match_id,
            team_id=serializer.validated_data["team_id"],
            players=players,
        )
    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    serializer = MatchListSerializer(data=result)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=MatchCommentRequestSerializer,
    responses={201: None},
    description="Add comments to match",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_comments(request, match_id):
    serializer = MatchCommentRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        comment = matches_service_client.add_comment(
            match_id=match_id,
            message=serializer.validated_data["message"],
            created_by=UUID(
                "00000000-0000-0000-0000-000000000000"
            ),  # TODO: Get from auth
        )
        return Response(comment, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF",
    tags=["Match Management"],
)
@api_view(["GET"])
def match_sheet(request, match_id):
    return Response({"message": "PDF generation not implemented"})


urlpatterns = [
    path("", MatchListCreateView.as_view(), name="match-list"),
    path("<uuid:match_id>/", MatchDetailView.as_view(), name="match-detail"),
    path("<uuid:match_id>/result/", match_result, name="match-result"),
    path("<uuid:match_id>/lineup/", match_lineup, name="match-lineup"),
    path("<uuid:match_id>/comments/", match_comments, name="match-comments"),
    path("<uuid:match_id>/sheet/", match_sheet, name="match-sheet"),
]
