"""
Tournament management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

# from ..serializers import (
#     TournamentCreateSerializer,
#     TournamentListSerializer,
#     TournamentUpdateSerializer,
# )
from ..models import Team, Tournament, TournamentRankingPosition, TournamentStatus


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.IntegerField(read_only=True)
    modality_name = serializers.CharField()
    name = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentDetailSerializer(TournamentListSerializer):
    """Serializer for tournament details"""

    teams = serializers.ListField(child=serializers.UUIDField(), required=False)


class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    modality_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    teams = serializers.ListField(child=serializers.UUIDField(), required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentUpdateSerializer(serializers.Serializer):
    """Serializer for updating a tournament"""

    name = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], required=False
    )
    teams_add = serializers.ListField(child=serializers.UUIDField(), required=False)
    teams_remove = serializers.ListField(child=serializers.UUIDField(), required=False)


class TournamentFinishSerializer(serializers.Serializer):
    """Serializer for finishing a tournament"""

    class TournamentFinishEntrySerializer(serializers.Serializer):
        """Serializer for finishing a tournament entry"""

        team_id = serializers.UUIDField(required=True)
        position = serializers.IntegerField(required=True)

    ranking_entries = TournamentFinishEntrySerializer(many=True)


# Mock database for tournaments
@extend_schema_view(
    get=extend_schema(
        responses=TournamentListSerializer(many=True),
        description="List all tournaments",
        tags=["Tournament Management"],
    ),
    post=extend_schema(
        request=TournamentCreateSerializer,
        responses=TournamentDetailSerializer,
        description="Create a new tournament",
        tags=["Tournament Management"],
    ),
)
class TournamentListCreateView(APIView):
    def get(self, request):
        """List all tournaments"""
        tournaments = Tournament.objects.all()
        return Response(
            [tournament.to_json() for tournament in tournaments],
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create a new tournament"""
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tornament = Tournament.objects.create(
            modality_id=serializer.validated_data["modality_id"],
            name=serializer.validated_data["name"],
            start_date=serializer.validated_data.get("start_date"),
            status=TournamentStatus.DRAFT,
            created_by="00000000-0000-0000-0000-000000000000",  # Placeholder
        )

        if "teams" in serializer.validated_data:
            for team_id in serializer.validated_data["teams"]:
                team = Team.objects.get(id=team_id)
                tornament.teams.add(team)

        return Response(tornament.to_json_detail(), status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        responses=TournamentDetailSerializer,
        description="Get tournament by ID",
        tags=["Tournament Management"],
    ),
    put=extend_schema(
        request=TournamentUpdateSerializer,
        responses=TournamentDetailSerializer,
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
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(tournament.to_json_detail(), status=status.HTTP_200_OK)

    def put(self, request, tournament_id):
        """Update a tournament"""
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if "name" in serializer.validated_data:
            tournament.name = serializer.validated_data["name"]
        if "start_date" in serializer.validated_data:
            tournament.start_date = serializer.validated_data["start_date"]
        if "status" in serializer.validated_data:
            tournament.status = serializer.validated_data["status"]
        if "teams_add" in serializer.validated_data:
            for team_id in serializer.validated_data["teams_add"]:
                team = Team.objects.get(id=team_id)
                tournament.teams.add(team)
        if "teams_remove" in serializer.validated_data:
            for team_id in serializer.validated_data["teams_remove"]:
                team = Team.objects.get(id=team_id)
                tournament.teams.remove(team)

        tournament.save()

        return Response(tournament.to_json_detail(), status=status.HTTP_200_OK)

    def delete(self, request, tournament_id):
        """Delete a tournament"""
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        tournament.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=TournamentFinishSerializer,
    responses={200: TournamentDetailSerializer},
    description="Finish a tournament",
    tags=["Tournament Management"],
)
@api_view(["POST"])
def tournament_finish(request, tournament_id):
    """Mark a tournament as finished"""
    serializer = TournamentFinishSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    tournament.ranking_positions.all().delete()
    for entry in serializer.validated_data["ranking_entries"]:
        team = Team.objects.get(id=entry["team_id"])
        position = entry["position"]
        TournamentRankingPosition.objects.create(
            tournament=tournament, team=team, position=position
        )

    tournament.status = TournamentStatus.FINISHED
    tournament.save()
    return Response(tournament.to_json_detail(), status=status.HTTP_200_OK)
