"""
Tournament management views - Updated to use tournaments-service microservice
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.tournaments_service import tournaments_service


class TournamentListSerializer(serializers.Serializer):
    """Serializer for listing tournaments"""

    id = serializers.UUIDField(read_only=True)
    modality_id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["draft", "active", "finished"], read_only=True
    )
    start_date = serializers.DateTimeField(required=False, allow_null=True)


class TournamentDetailSerializer(TournamentListSerializer):
    """Serializer for tournament details"""

    created_by = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    finished_at = serializers.DateTimeField(read_only=True, allow_null=True)
    finished_by = serializers.UUIDField(read_only=True, allow_null=True)
    ranking_positions = serializers.ListField(required=False, read_only=True)


class TournamentCreateSerializer(serializers.Serializer):
    """Serializer for creating a tournament"""

    modality_id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    team_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
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
        try:
            # Call microservice
            tournaments = tournaments_service.list_tournaments()
            return Response(tournaments, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new tournament"""
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Call microservice
            tournament = tournaments_service.create_tournament(
                modality_id=serializer.validated_data["modality_id"],
                name=serializer.validated_data["name"],
                created_by="00000000-0000-0000-0000-000000000000",  # Placeholder
                start_date=(
                    serializer.validated_data.get("start_date").isoformat()
                    if serializer.validated_data.get("start_date")
                    else None
                ),
                team_ids=serializer.validated_data.get("team_ids"),
            )
            return Response(tournament, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            tournament = tournaments_service.get_tournament(tournament_id)
            return Response(tournament, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, tournament_id):
        """Update a tournament"""
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Call microservice
            tournament = tournaments_service.update_tournament(
                tournament_id=tournament_id,
                name=serializer.validated_data.get("name"),
                start_date=(
                    serializer.validated_data.get("start_date").isoformat()
                    if serializer.validated_data.get("start_date")
                    else None
                ),
                status=serializer.validated_data.get("status"),
                teams_add=serializer.validated_data.get("teams_add"),
                teams_remove=serializer.validated_data.get("teams_remove"),
            )
            return Response(tournament, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, tournament_id):
        """Delete a tournament"""
        try:
            tournaments_service.delete_tournament(tournament_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        # Prepare ranking entries
        ranking_entries = [
            {"team_id": str(entry["team_id"]), "position": entry["position"]}
            for entry in serializer.validated_data["ranking_entries"]
        ]

        # Call microservice
        tournament = tournaments_service.finish_tournament(
            tournament_id=tournament_id,
            ranking_entries=ranking_entries,
            finished_by="00000000-0000-0000-0000-000000000000",  # Placeholder
        )
        return Response(tournament, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
