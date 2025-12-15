"""
{
    "id": 1,
    "tournament_id": 1,
    "tournament_name": "Campeonato de Futebol 25/26",
    "team_home": {
        "id": 1,
        "name": "NEI",
        "course_abbreviation": "NEI"
    },
    "team_away": {
        "id": 2,
        "name": "NEC",
        "course_abbreviation": "NEC"
    },
    "modality": {
        "id": 1,
        "name": "Futebol"
    },
    "start_time": "2025-12-03T14:00:00",
    "location": "Pavilhão Gimnodesportivo da UA",
    "status": "finished",
    "home_score": 2,
    "away_score": 1
}
"""

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Match, Modality


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


"""
Modality {
  id: number;
  name: string;
  type: string;
  scoring_schema?: Record<string, number>;
}
"""


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
