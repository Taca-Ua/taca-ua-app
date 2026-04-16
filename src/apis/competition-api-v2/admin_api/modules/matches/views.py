"""
Match management views
"""

from uuid import UUID

import structlog
from django.http import HttpResponse
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CommentCreateSerializer,
    LineupAssignSerializer,
    MatchCreateSerializer,
    MatchDetailSerializer,
    MatchListFilterSerializer,
    MatchListSerializer,
    MatchPublishResultsSerializer,
    MatchUpdateSerializer,
)
from .service import matches_service

logger = structlog.get_logger(__name__)


@extend_schema_view(
    get=extend_schema(
        parameters=[MatchListFilterSerializer],
        responses=MatchListSerializer(many=True),
        description="List all matches with optional filters",
        tags=["Match Management"],
    ),
    post=extend_schema(
        request=MatchCreateSerializer,
        responses=MatchListSerializer,
        description="Create a new match with participants",
        tags=["Match Management"],
    ),
)
class MatchListCreateView(APIView):
    """List and create matches"""

    def get(self, request):
        """List matches with optional filters"""
        # Extract query parameters for filtering
        tournament_id = request.query_params.get("tournament_id")
        status_filter = request.query_params.get("status")

        matches = matches_service.list_matches(
            tournament_id=UUID(tournament_id) if tournament_id else None,
            status=status_filter if status_filter else None,
        )

        serializer = MatchListSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new match"""
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Prepare participants if provided
        match = matches_service.create_match(
            tournament_id=serializer.validated_data.get("tournament_id"),
            location=serializer.validated_data.get("location"),
            start_time=serializer.validated_data.get("start_time").isoformat(),
            participants_ids=[
                str(competitor)
                for competitor in serializer.validated_data.get("competitors", [])
            ],
        )

        response_serializer = MatchListSerializer(match)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


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
class MatchDetailView(APIView):
    """Retrieve, update, or delete a match"""

    def get(self, request, match_id):
        """Get match details"""

        match = matches_service.get_match(match_id=match_id)

        serializer = MatchDetailSerializer(match)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, match_id):
        """Update match metadata"""
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match = matches_service.update_match(
            match_id=match_id,
            location=serializer.validated_data.get("location"),
            start_time=(
                serializer.validated_data.get("start_time").isoformat()
                if serializer.validated_data.get("start_time")
                else None
            ),
            status=serializer.validated_data.get("status"),
        )

        response_serializer = MatchDetailSerializer(match)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, match_id):
        """Delete a match"""

        matches_service.delete_match(match_id=match_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=MatchPublishResultsSerializer,
    responses=MatchDetailSerializer,
    description="Publish match results for all participants (scores and/or positions)",
    tags=["Match Management"],
)
@api_view(["POST"])
def publish_match_results(request, match_id):
    """Publish match results"""
    serializer = MatchPublishResultsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Prepare participant results
    participant_results = []
    for result_data in serializer.validated_data["participant_results"]:
        result = {"participant": str(result_data["participant"])}
        if result_data.get("score") is not None:
            result["score"] = result_data["score"]
        if result_data.get("position") is not None:
            result["position"] = result_data["position"]
        participant_results.append(result)

    match = matches_service.publish_match_results(
        match_id=match_id,
        participant_results=participant_results,
    )

    response_serializer = MatchDetailSerializer(match)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


# ============= Lineup Management Views =============


@extend_schema(
    request=LineupAssignSerializer,
    responses={"message": "string"},
    description="Assign lineup for a team in a match",
    tags=["Match Management"],
)
@api_view(["POST"])
def assign_lineup(request, match_id):
    """Assign lineup for a team"""
    serializer = LineupAssignSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Convert serializer data to service format
    players = [
        {
            "player": str(player_data["player"]),
            "jersey_number": player_data.get("jersey_number"),
            "is_starter": player_data.get("is_starter", True),
        }
        for player_data in serializer.validated_data["players"]
    ]

    matches_service.assign_lineup(
        match_id=match_id,
        participant=str(serializer.validated_data["participant"]),
        players=players,
    )

    return Response(
        {"message": "Lineup assigned successfully"}, status=status.HTTP_200_OK
    )


# ============= Comment Management Views =============


@extend_schema(
    request=CommentCreateSerializer,
    responses=MatchDetailSerializer,
    description="Add a comment to a match",
    tags=["Match Management"],
)
@api_view(["POST"])
def add_comment(request, match_id):
    """Add comment to match"""
    serializer = CommentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    match = matches_service.add_comment(
        match_id=match_id,
        message=serializer.validated_data["message"],
    )

    response_serializer = MatchDetailSerializer(match)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={204: None},
    description="Delete a comment from a match",
    tags=["Match Management"],
)
@api_view(["DELETE"])
def delete_comment(request, match_id, comment_id):
    """Delete a comment"""
    matches_service.delete_comment(match_id=match_id, comment_id=comment_id)
    return Response(status=status.HTTP_204_NO_CONTENT)


# ============= Additional Endpoints =============


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF",
    tags=["Match Management"],
)
@api_view(["GET"])
def match_sheet(request, match_id):
    """Generate match sheet PDF"""

    pdf_content = matches_service.generate_match_report(match_id=match_id)

    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="match_sheet_{match_id}.pdf"'
    )
    return response


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF for a specific team",
    tags=["Match Management"],
)
@api_view(["GET"])
def match_team_sheet(request, match_id, participant):
    """
    Generate match sheet PDF for a specific team in a match.
    """

    pdf_content = matches_service.generate_match_team_report(
        match_id, participant=str(participant)
    )

    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="match_team_sheet_{match_id}_{participant}.pdf"'
    )
    return response


# ============= URL Patterns =============


urlpatterns = [
    # Match CRUD
    path("", MatchListCreateView.as_view(), name="match-list-create"),
    path("<uuid:match_id>/", MatchDetailView.as_view(), name="match-detail"),
    # Match results
    path(
        "<uuid:match_id>/results/", publish_match_results, name="publish-match-results"
    ),
    # Lineup management
    path("<uuid:match_id>/lineup/", assign_lineup, name="match-lineup"),
    # Comment management
    path("<uuid:match_id>/comments/", add_comment, name="match-add-comment"),
    path(
        "<uuid:match_id>/comments/<uuid:comment_id>/",
        delete_comment,
        name="match-delete-comment",
    ),
    # Additional features
    path("<uuid:match_id>/match-sheet/", match_sheet, name="match-sheet"),
    path(
        "<uuid:match_id>/team-sheet/<uuid:participant>/",
        match_team_sheet,
        name="match-team-sheet",
    ),
]
