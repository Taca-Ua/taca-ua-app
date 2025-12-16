from collections import defaultdict
from typing import List

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import (
    Course,
    Match,
    Modality,
    Tournament,
    TournamentRankingPosition,
    TournamentStatus,
)

SEASON_ID = 1
SEASON_YEAR = 2024


class GetMatchesParamsSerializer(serializers.Serializer):
    """Serializer for the GET parameters of the matches endpoint"""

    date = serializers.DateField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    modality_id = serializers.UUIDField(required=False)
    course_id = serializers.UUIDField(required=False)
    team_id = serializers.UUIDField(required=False)
    status = serializers.CharField(required=False)


@extend_schema(
    request=GetMatchesParamsSerializer(),
    responses=serializers.ListSerializer(child=serializers.DictField()),
    description="Endpoint to get public calendar of tournaments and matches.",
    tags=["Public API"],
)
@api_view(["GET"])
def calendar(request):
    """Endpoint to get public calendar of tournaments and matches."""
    serializers = GetMatchesParamsSerializer(data=request.query_params)
    serializers.is_valid(raise_exception=True)

    matchs = Match.objects.all()

    return Response(
        [
            {
                "id": match.id,
                "tournament_id": match.tournament.id,
                "tournament_name": match.tournament.name,
                "team_home": {
                    "id": match.team_home.id,
                    "name": match.team_home.name,
                    "course_abbreviation": match.team_home.course.abbreviation,
                },
                "team_away": {
                    "id": match.team_away.id,
                    "name": match.team_away.name,
                    "course_abbreviation": match.team_away.course.abbreviation,
                },
                "modality": {
                    "id": match.tournament.modality.id,
                    "name": match.tournament.modality.name,
                },
                "start_time": match.start_time,
                "location": match.location,
                "status": match.status,
                "home_score": match.home_score,
                "away_score": match.away_score,
            }
            for match in matchs
        ],
        status=status.HTTP_200_OK,
    )


class ModalitySerializer(serializers.Serializer):
    """Serializer for Modality model"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    type = serializers.CharField()


@extend_schema(
    responses=ModalitySerializer(many=True),
    description="Endpoint to get the list of modalities.",
    tags=["Public API"],
)
@api_view(["GET"])
def modality_list(_request):
    """Endpoint to get the list of modalities."""
    modalities = Modality.objects.all()

    return Response(
        [
            {
                "id": modality.id,
                "name": modality.name,
                "type": modality.modality_type.name,
            }
            for modality in modalities
        ],
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses=dict,
    description="Endpoint to get general rankings per Course for a given season.",
    tags=["Public API"],
)
@api_view(["GET"])
def rankings_general(request):
    """
    General ranking per Course.

    Rules:
    - A Course earns points from tournaments
    - Teams belong to a Course
    - If multiple teams from the same Course participate in a tournament,
      only the best positioned team counts
    - Points are assigned using tournament escaloes
    """

    # TODO: replace with real season logic when available

    # Load all ranking positions efficiently
    ranking_positions = TournamentRankingPosition.objects.select_related(
        "team",
        "team__course",
        "tournament",
        "tournament__modality",
        "tournament__modality__modality_type",
    ).prefetch_related("tournament__teams")

    # (tournament_id, course_id) -> (best_position, tournament)
    best_positions = {}

    for rp in ranking_positions:
        team = rp.team
        course = getattr(team, "course", None)

        if course is None:
            continue

        key = (rp.tournament_id, course.id)

        if key not in best_positions or rp.position < best_positions[key][0]:
            best_positions[key] = (rp.position, rp.tournament)

    # Sum points per course
    course_points = defaultdict(int)

    for (_, course_id), (position, tournament) in best_positions.items():
        points = tournament.get_points_for_position(position)
        course_points[course_id] += points

    # Load courses in bulk
    courses: List[Course] = Course.objects.all()

    # Build ranking list
    rankings = [
        {
            "course_id": str(course.id),
            "course_name": course.name,
            "points": course_points.get(course.id, 0),
        }
        for course in courses
    ]

    # Sort by points desc
    rankings.sort(key=lambda x: x["points"], reverse=True)

    return Response(
        {
            "season_id": SEASON_ID,
            "season_year": SEASON_YEAR,
            "rankings": rankings,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses=serializers.ListSerializer(child=serializers.DictField()),
    description="Endpoint to get the list of public seasons.",
    tags=["Public API"],
)
@api_view(["GET"])
def public_season_list(request):
    """Endpoint to get the list of public seasons."""

    return Response(
        [
            {
                "id": 1,
                "year": 2023,
                "status": "draft",
            }
        ],
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses=serializers.ListSerializer(child=serializers.DictField()),
    description="Endpoint to get the list of tournaments.",
    tags=["Public API"],
)
@api_view(["GET"])
def tournaments_public(request):
    """Endpoint to get the list of tournaments."""
    tournaments = Tournament.objects.filter(status=TournamentStatus.FINISHED)

    return Response(
        [
            {
                "id": str(tournament.id),
                "name": tournament.name,
                "modality": {
                    "id": str(tournament.modality.id),
                    "name": tournament.modality.name,
                },
                "season": {
                    "id": SEASON_ID,
                    "year": SEASON_YEAR,
                },
                "status": tournament.status,
                "start_date": tournament.start_date,
                "team_count": tournament.teams.count(),
                "rankings": tournament.get_final_rankings(),
            }
            for tournament in tournaments
        ],
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses=serializers.DictField(),
    description="Endpoint to get the tournaments.",
    tags=["Public API"],
)
@api_view(["GET"])
def get_tournament_public(request, tournament_id):
    """Endpoint to get the tournaments."""
    try:
        tournament = Tournament.objects.get(
            id=tournament_id, status=TournamentStatus.FINISHED
        )
    except Tournament.DoesNotExist:
        return Response(
            {"detail": "Tournament not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {
            "id": str(tournament.id),
            "name": tournament.name,
            "modality": {
                "id": str(tournament.modality.id),
                "name": tournament.modality.name,
            },
            "season": {
                "id": SEASON_ID,
                "year": SEASON_YEAR,
            },
            "status": tournament.status,
            "start_date": tournament.start_date,
            "team_count": tournament.teams.count(),
            "rankings": tournament.get_final_rankings(),
        },
        status=status.HTTP_200_OK,
    )
