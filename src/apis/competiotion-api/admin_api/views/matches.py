"""
Match management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Match, Team, Tournament
from ..serializers import (  # MatchCreateSerializer,; MatchListSerializer,; MatchUpdateSerializer,
    MatchCommentSerializer,
    MatchLineupSerializer,
    MatchResultSerializer,
)


class MatchListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    team_home_name = serializers.CharField()
    team_away_name = serializers.CharField()
    location = serializers.CharField()
    start_time = serializers.DateTimeField()
    status = serializers.CharField()

    home_score = serializers.IntegerField(required=False)
    away_score = serializers.IntegerField(required=False)


class MatchCreateSerializer(serializers.Serializer):
    tournament_id = serializers.UUIDField()
    team_home_id = serializers.UUIDField()
    team_away_id = serializers.UUIDField()
    location = serializers.CharField()
    start_time = serializers.DateTimeField()


class MatchUpdateSerializer(serializers.Serializer):
    location = serializers.CharField(required=False)
    start_time = serializers.DateTimeField(required=False)
    status = serializers.CharField(required=False)
    home_score = serializers.IntegerField(required=False)
    away_score = serializers.IntegerField(required=False)


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
        matchs = Match.objects.all()
        return Response(
            [match.to_json() for match in matchs], status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = MatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the match
        match = Match.objects.create(
            team_home=Team.objects.get(id=serializer.validated_data["team_home_id"]),
            team_away=Team.objects.get(id=serializer.validated_data["team_away_id"]),
            location=serializer.validated_data["location"],
            start_time=serializer.validated_data["start_time"],
            created_by="00000000-0000-0000-0000-000000000000",
        )

        # Add the match to the tournament's matches
        try:
            tournament = Tournament.objects.get(
                id=serializer.validated_data["tournament_id"]
            )
            tournament.matches.add(match)
            tournament.save()
        except Tournament.DoesNotExist:
            match.delete()  # Clean up the created match
            return Response(
                {"detail": "Tournament not found."}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            match.delete()  # Clean up the created match
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(match.to_json(), status=status.HTTP_201_CREATED)


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
        match = Match.objects.get(id=match_id)

        return Response(match.to_json(), status=status.HTTP_200_OK)

    def put(self, request, match_id):
        serializer = MatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        match = Match.objects.get(id=match_id)

        if "location" in serializer.validated_data:
            match.location = serializer.validated_data["location"]
        if "start_time" in serializer.validated_data:
            match.start_time = serializer.validated_data["start_time"]
        if "status" in serializer.validated_data:
            match.status = serializer.validated_data["status"]

        # scores must be provided together
        if not all(
            field in serializer.validated_data for field in ("home_score", "away_score")
        ):
            raise serializers.ValidationError(
                "Both home_score and away_score must be provided together."
            )
        else:
            match.home_score = serializer.validated_data["home_score"]
            match.away_score = serializer.validated_data["away_score"]

        match.save()
        return Response(match.to_json(), status=status.HTTP_200_OK)

    def delete(self, request, match_id):
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=MatchResultSerializer,
    responses=MatchListSerializer,
    description="Register match result",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_result(request, match_id):
    serializer = MatchResultSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({}, status=status.HTTP_200_OK)


@extend_schema(
    request=MatchLineupSerializer,
    responses={200: None},
    description="Assign players to match lineup",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_lineup(request, match_id):
    serializer = MatchLineupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({}, status=status.HTTP_200_OK)


@extend_schema(
    request=MatchCommentSerializer,
    responses={201: None},
    description="Add comments to match",
    tags=["Match Management"],
)
@api_view(["POST"])
def match_comments(request, match_id):
    serializer = MatchCommentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({}, status=status.HTTP_201_CREATED)


@extend_schema(
    responses={200: {"type": "string", "format": "binary"}},
    description="Generate match sheet PDF",
    tags=["Match Management"],
)
@api_view(["GET"])
def match_sheet(request, match_id):
    return Response({"message": "PDF generation not implemented"})
