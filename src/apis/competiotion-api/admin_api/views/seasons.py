"""
Season management views
"""

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators import RoleRequiredMixin, require_auth
from ..serializers.seasons import SeasonCreateSerializer, SeasonListSerializer
from ..services.seasons_service import seasons_service_client


@extend_schema_view(
    get=extend_schema(
        responses=SeasonListSerializer(many=True),
        description="List all seasons",
        tags=["Season Management"],
    ),
    post=extend_schema(
        request=SeasonCreateSerializer,
        responses=SeasonListSerializer,
        description="Create a new season",
        tags=["Season Management"],
    ),
)
class SeasonListCreateView(RoleRequiredMixin, APIView):
    def get(self, request):
        seasons = seasons_service_client.list_seasons()
        serializer = SeasonListSerializer(
            [vars(s) for s in seasons], many=True
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        season = seasons_service_client.create_season(
            year=serializer.validated_data["year"]
        )
        return Response(vars(season), status=status.HTTP_201_CREATED)


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Start a season",
    tags=["Season Management"],
)
@api_view(["POST"])
@require_auth
def season_start(request, season_id):
    season = seasons_service_client.start_season(season_id)
    return Response(vars(season))


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Finish a season. Fails if any tournament in the season is still open.",
    tags=["Season Management"],
)
@api_view(["POST"])
@require_auth
def season_finish(request, season_id):
    season = seasons_service_client.finish_season(season_id)
    return Response(vars(season))


urlpatterns = [
    path("", SeasonListCreateView.as_view(), name="season-list"),
    path("<uuid:season_id>/start/", season_start, name="season-start"),
    path("<uuid:season_id>/finish/", season_finish, name="season-finish"),
]
