"""
Tournament management views - Updated to use tournaments-service microservice
"""

from admin_api.utils.decorators import (
    RoleRequiredMixin,
    require_roles,
    require_roles_class_method,
)
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    TournamentCompetitorsAddEntrySerializer,
    TournamentCompetitorsDeleteSerializer,
    TournamentCreateSerializer,
    TournamentDetailSerializer,
    TournamentFinishSerializer,
    TournamentListQuerySerializer,
    TournamentListSerializer,
    TournamentUpdateSerializer,
)
from .service import TeamDoesNotBelongToSeasonError, tournaments_service


@extend_schema_view(
    get=extend_schema(
        parameters=[TournamentListQuerySerializer],
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
class TournamentListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        """List all tournaments"""
        serializer = TournamentListQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        tournaments = tournaments_service.list_tournaments(
            status=serializer.validated_data.get("status", None),
            modality_id=serializer.validated_data.get("modality_id", None),
            season_id=serializer.validated_data.get("season_id", None),
        )

        serializer = TournamentListSerializer(tournaments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def post(self, request):
        """Create a new tournament"""
        serializer = TournamentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tournament = tournaments_service.create_tournament(
            name=serializer.validated_data["name"],
            modality_id=serializer.validated_data["modality_id"],
            season_id=serializer.validated_data.get("season_id", None),
            scoring_format_id=serializer.validated_data.get("scoring_format_id", None),
        )

        serializer = TournamentListSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
class TournamentDetailView(RoleRequiredMixin, APIView):
    def get(self, request, tournament_id):
        """Get tournament details by ID"""
        tournament = tournaments_service.get_tournament(tournament_id)

        serializer = TournamentDetailSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def put(self, request, tournament_id):
        """Update a tournament"""
        serializer = TournamentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_date = serializer.validated_data.get("start_date", None)
        if updated_date is not None:
            updated_date = updated_date.isoformat()

        tournament = tournaments_service.update_tournament(
            tournament_id=tournament_id,
            name=serializer.validated_data.get("name", None),
            start_date=updated_date,
            status=serializer.validated_data.get("status", None),
            is_playoff=serializer.validated_data.get("is_playoff", None),
        )

        serializer = TournamentDetailSerializer(tournament)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @require_roles_class_method("general_admin")
    def delete(self, request, tournament_id):
        """Delete a tournament"""
        try:
            tournaments_service.delete_tournament(tournament_id)
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=TournamentFinishSerializer,
    responses={200: TournamentDetailSerializer},
    description="Finish a tournament",
    tags=["Tournament Management"],
)
@api_view(["POST"])
@require_roles("general_admin")
def tournament_finish(request, tournament_id):
    """Mark a tournament as finished"""
    serializer = TournamentFinishSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Prepare ranking entries - extract competitor_id based on type
    ranking_entries = []
    for entry in serializer.validated_data["ranking_entries"]:
        ranking_entries.append(
            {
                "competitor_id": str(entry["competitor_id"]),
                "position": entry["position"],
            }
        )

    tournament = tournaments_service.finish_tournament(
        tournament_id=tournament_id,
        ranking_entries=ranking_entries,
    )

    serializer = TournamentDetailSerializer(tournament)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=TournamentCompetitorsAddEntrySerializer(many=True),
    responses={200: TournamentDetailSerializer},
    description="Add competitors to a tournament",
    tags=["Tournament Management"],
)
@api_view(["PUT"])
@require_roles("general_admin")
def tournament_add_competitors(request, tournament_id):
    """Add competitors to a tournament"""
    serializer = TournamentCompetitorsAddEntrySerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)

    extracted_competitors_data = []
    for competitor in serializer.validated_data:
        extracted_competitors_data.append(
            {
                "competitor_type": competitor["competitor_type"],
                "entity_id": str(competitor["entity_id"]),
            }
        )

    try:
        tournament = tournaments_service.add_competitors(
            tournament_id=tournament_id,
            competitors_data=extracted_competitors_data,
        )
    except TeamDoesNotBelongToSeasonError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise e

    serializer = TournamentDetailSerializer(tournament)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=TournamentCompetitorsDeleteSerializer,
    responses={200: TournamentDetailSerializer},
    description="Remove competitors from a tournament",
    tags=["Tournament Management"],
)
@api_view(["PUT"])
@require_roles("general_admin")
def tournament_remove_competitors(request, tournament_id):
    """Remove competitors from a tournament"""
    serializer = TournamentCompetitorsDeleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    tournament = tournaments_service.remove_competitors(
        tournament_id=tournament_id,
        competitor_ids=serializer.validated_data["competitors_ids"],
    )

    serializer = TournamentDetailSerializer(tournament)
    return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("", TournamentListCreateView.as_view(), name="tournament-list"),
    path(
        "<uuid:tournament_id>/",
        TournamentDetailView.as_view(),
        name="tournament-detail",
    ),
    path(
        "<uuid:tournament_id>/finish/",
        tournament_finish,
        name="tournament-finish",
    ),
    path(
        "<uuid:tournament_id>/competitors/add/",
        tournament_add_competitors,
        name="tournament-add-competitors",
    ),
    path(
        "<uuid:tournament_id>/competitors/remove/",
        tournament_remove_competitors,
        name="tournament-remove-competitors",
    ),
]
