"""
Match management views
"""

from uuid import UUID

import structlog
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators import RoleRequiredMixin, require_auth
from ..serializers.matches import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    LineupAssignSerializer,
    LineupDetailSerializer,
    MatchCreateSerializer,
    MatchDetailSerializer,
    MatchListSerializer,
    MatchResultsUpdateSerializer,
    MatchUpdateSerializer,
    ParticipantCreateSerializer,
    ParticipantDetailSerializer,
)
from ..services.enricher_service import enricher_service
from ..services.matches_service import matches_service_client

logger = structlog.get_logger(__name__)


# ============= Match CRUD Views =============


@extend_schema_view(
    get=extend_schema(
        responses=MatchListSerializer(many=True),
        description="List all matches with optional filters",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=MatchCreateSerializer,
        responses=MatchDetailSerializer,
        description="Create a new match with participants",
        tags=["Match Management"],
    ),
)
class MatchListCreateView(RoleRequiredMixin, APIView):
    """List and create matches"""

    def get(self, request):
        """List matches with optional filters"""
        # Extract query parameters for filtering
        tournament_id = request.query_params.get("tournament_id")
        team_id = request.query_params.get("team_id")
        athlete_id = request.query_params.get("athlete_id")
        status_filter = request.query_params.get("status")
        date = request.query_params.get("date")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        try:
            matches = matches_service_client.list_matches(
                tournament_id=UUID(tournament_id) if tournament_id else None,
                team_id=UUID(team_id) if team_id else None,
                athlete_id=UUID(athlete_id) if athlete_id else None,
                status=status_filter,
                date=date,
                date_from=date_from,
                date_to=date_to,
            )

            # Enrich participant data with team/athlete details
            enricher_service.complete_matches_info(matches)

            serializer = MatchListSerializer(matches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Failed to list matches", error=str(e))
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new match"""
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Prepare participants if provided
        participants = []
        if serializer.validated_data.get("participants"):
            for participant_data in serializer.validated_data["participants"]:
                participant = {"participant_type": participant_data["participant_type"]}
                if participant_data.get("team_id"):
                    participant["team_id"] = str(participant_data["team_id"])
                if participant_data.get("athlete_id"):
                    participant["athlete_id"] = str(participant_data["athlete_id"])
                participants.append(participant)

        try:
            match = matches_service_client.create_match(
                tournament_id=serializer.validated_data.get("tournament_id"),
                location=serializer.validated_data["location"],
                start_time=serializer.validated_data["start_time"].isoformat(),
                created_by=UUID("00000000-0000-0000-0000-000000000000"),  # TODO: Auth
                participants=participants if participants else None,
            )

            # Enrich participant data
            enricher_service.complete_matches_info([match])

            response_serializer = MatchDetailSerializer(match)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Failed to create match", error=str(e))
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        responses=MatchDetailSerializer,
        description="Get detailed information about a specific match",
        tags=["Match Management"],
    ),
    put=extend_schema(
        request=MatchUpdateSerializer,
        responses=MatchDetailSerializer,
        description="Update match metadata (location, start time, status)",
        tags=["Match Management"],
    ),
    delete=extend_schema(
        responses={204: None},
        description="Delete a match",
        tags=["Match Management"],
    ),
)
class MatchDetailView(RoleRequiredMixin, APIView):
    """Retrieve, update, or delete a match"""

    def get(self, request, match_id):
        """Get match details"""
        try:
            match = matches_service_client.get_match(match_id=match_id)
            print("Match fetched:", match.__dict__["participants"])

            # Enrich participant data
            enricher_service.complete_matches_info([match])

            serializer = MatchDetailSerializer(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Failed to get match", match_id=str(match_id), error=str(e))
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, match_id):
        """Update match metadata"""
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

        try:
            match = matches_service_client.update_match(
                match_id=match_id, **update_data
            )

            # Enrich participant data
            enricher_service.complete_matches_info([match])

            response_serializer = MatchDetailSerializer(match)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Failed to update match", match_id=str(match_id), error=str(e))
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, match_id):
        """Delete a match"""
        try:
            matches_service_client.delete_match(match_id=match_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error("Failed to delete match", match_id=str(match_id), error=str(e))
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


# ============= Participant Management Views =============


@extend_schema_view(
    post=extend_schema(
        request=ParticipantCreateSerializer,
        responses=ParticipantDetailSerializer,
        description="Add a participant (team or athlete) to a match",
        tags=["Match Management"],
    ),
)
class ParticipantAddView(RoleRequiredMixin, APIView):
    """Add a participant to a match"""

    def post(self, request, match_id):
        """Add participant to match"""
        serializer = ParticipantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            participant = matches_service_client.add_participant(
                match_id=match_id,
                participant_type=serializer.validated_data["participant_type"],
                team_id=serializer.validated_data.get("team_id"),
                athlete_id=serializer.validated_data.get("athlete_id"),
            )

            # Enrich participant data
            enricher_service.complete_participant_info([participant])

            response_serializer = ParticipantDetailSerializer(participant)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(
                "Failed to add participant", match_id=str(match_id), error=str(e)
            )
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    responses={204: None},
    description="Remove a participant from a match",
    tags=["Match Management"],
)
@api_view(["DELETE"])
@require_auth
def remove_participant(request, match_id, participant_id):
    """Remove participant from match"""
    try:
        matches_service_client.remove_participant(
            match_id=match_id, participant_id=participant_id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(
            "Failed to remove participant",
            match_id=str(match_id),
            participant_id=str(participant_id),
            error=str(e),
        )
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


# ============= Match Results Views =============


@extend_schema(
    request=MatchResultsUpdateSerializer,
    responses=MatchDetailSerializer,
    description="Update match results for all participants (scores and/or positions)",
    tags=["Match Management"],
)
@api_view(["PUT"])
@require_auth
def update_match_results(request, match_id):
    """Update match results"""
    serializer = MatchResultsUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Prepare participant results
    participant_results = []
    for result_data in serializer.validated_data["participant_results"]:
        result = {"participant_id": str(result_data["participant_id"])}
        if result_data.get("score") is not None:
            result["score"] = result_data["score"]
        if result_data.get("position") is not None:
            result["position"] = result_data["position"]
        if result_data.get("result_metadata"):
            result["result_metadata"] = result_data["result_metadata"]
        participant_results.append(result)

    try:
        match = matches_service_client.update_match_results(
            match_id=match_id,
            participant_results=participant_results,
            status=serializer.validated_data.get("status", "finished"),
        )

        # Enrich participant data
        enricher_service.complete_matches_info([match])

        response_serializer = MatchDetailSerializer(match)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(
            "Failed to update match results", match_id=str(match_id), error=str(e)
        )
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============= Lineup Management Views =============


@extend_schema_view(
    get=extend_schema(
        responses=LineupDetailSerializer(many=True),
        description="Get lineup for a match, optionally filtered by team",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=LineupAssignSerializer,
        responses={"message": "string"},
        description="Assign lineup for a team in a match",
        tags=["Match Management"],
    ),
)
class LineupView(RoleRequiredMixin, APIView):
    """Get or assign lineup for a match"""

    def get(self, request, match_id):
        """Get lineup for match"""
        team_id = request.query_params.get("team_id")

        try:
            lineup = matches_service_client.get_lineup(
                match_id=match_id, team_id=UUID(team_id) if team_id else None
            )

            # Enrich player data
            enricher_service.complete_lineup_info(lineup)

            serializer = LineupDetailSerializer(lineup, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Failed to get lineup", match_id=str(match_id), error=str(e))
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, match_id):
        """Assign lineup for a team"""
        serializer = LineupAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Convert serializer data to service format
        players = [
            {
                "player_id": str(player_data["player_id"]),
                "jersey_number": player_data["jersey_number"],
                "is_starter": player_data.get("is_starter", True),
            }
            for player_data in serializer.validated_data["players"]
        ]

        try:
            result = matches_service_client.assign_lineup(
                match_id=match_id,
                team_id=serializer.validated_data["team_id"],
                players=players,
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                "Failed to assign lineup", match_id=str(match_id), error=str(e)
            )
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============= Comment Management Views =============


@extend_schema_view(
    get=extend_schema(
        responses=CommentDetailSerializer(many=True),
        description="Get all comments for a match",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=CommentCreateSerializer,
        responses=CommentDetailSerializer,
        description="Add a comment to a match",
        tags=["Match Management"],
    ),
)
class CommentView(RoleRequiredMixin, APIView):
    """Get or add comments for a match"""

    def get(self, request, match_id):
        """Get all comments for match"""
        try:
            comments = matches_service_client.get_comments(match_id=match_id)
            serializer = CommentDetailSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Failed to get comments", match_id=str(match_id), error=str(e))
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, match_id):
        """Add comment to match"""
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            comment = matches_service_client.add_comment(
                match_id=match_id,
                message=serializer.validated_data["message"],
                created_by=UUID("00000000-0000-0000-0000-000000000000"),  # TODO: Auth
            )
            response_serializer = CommentDetailSerializer(comment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error("Failed to add comment", match_id=str(match_id), error=str(e))
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    responses={204: None},
    description="Delete a comment from a match",
    tags=["Match Management"],
)
@api_view(["DELETE"])
@require_auth
def delete_comment(request, match_id, comment_id):
    """Delete a comment"""
    try:
        matches_service_client.delete_comment(match_id=match_id, comment_id=comment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(
            "Failed to delete comment",
            match_id=str(match_id),
            comment_id=str(comment_id),
            error=str(e),
        )
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


# ============= Additional Endpoints =============


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF (not implemented yet)",
    tags=["Match Management"],
)
@api_view(["GET"])
@require_auth
def match_sheet(request, match_id):
    """Generate match sheet PDF"""
    return Response(
        {"message": "PDF generation not implemented"},
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )


# ============= URL Patterns =============


urlpatterns = [
    # Match CRUD
    path("", MatchListCreateView.as_view(), name="match-list-create"),
    path("<uuid:match_id>/", MatchDetailView.as_view(), name="match-detail"),
    # Participant management
    path(
        "<uuid:match_id>/participants/",
        ParticipantAddView.as_view(),
        name="match-add-participant",
    ),
    path(
        "<uuid:match_id>/participants/<uuid:participant_id>/",
        remove_participant,
        name="match-remove-participant",
    ),
    # Match results
    path(
        "<uuid:match_id>/results/",
        update_match_results,
        name="match-update-results",
    ),
    # Lineup management
    path("<uuid:match_id>/lineup/", LineupView.as_view(), name="match-lineup"),
    # Comment management
    path("<uuid:match_id>/comments/", CommentView.as_view(), name="match-comments"),
    path(
        "<uuid:match_id>/comments/<uuid:comment_id>/",
        delete_comment,
        name="match-delete-comment",
    ),
    # Additional features
    path("<uuid:match_id>/sheet/", match_sheet, name="match-sheet"),
]
