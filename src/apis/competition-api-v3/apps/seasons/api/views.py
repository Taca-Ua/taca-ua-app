from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import (
    RoleRequiredMixin,
    require_auth,
    require_roles_class_method,
)
from shared.auth.utils import RolesEnum, get_user

from ..selectors import (
    get_current_season,
    get_season_by_id,
    get_season_summary_by_id,
    get_seasons_table,
)
from ..service import create_season
from .serializers import (
    SeasonCreateSerializer,
    SeasonListSerializer,
    SeasonSummarySerializer,
)


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
        seasons = get_seasons_table()

        serializer = SeasonListSerializer(seasons, many=True)
        return Response(serializer.data)

    @require_roles_class_method(RolesEnum.GENERAL_ADMIN)
    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_user(request)

        season = create_season(
            name=serializer.validated_data["name"], admin_id=user.user_id
        )

        serializer = SeasonListSerializer(get_season_by_id(season.id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    responses=SeasonListSerializer,
    description="Get current season",
    tags=["Season Management"],
)
@api_view(["GET"])
@require_auth
def get_current_season_view(request):
    season = get_current_season()

    if not season:
        return Response(
            {"detail": "No active season found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = SeasonListSerializer(season)
    return Response(serializer.data)


@extend_schema(
    responses=SeasonSummarySerializer,
    description="Get season summary",
    tags=["Season Management"],
)
@api_view(["GET"])
@require_auth
def get_season_summary_view(request, season_id):
    user = get_user(request)

    season = get_season_summary_by_id(
        season_id,
        admin_id=user.user_id if RolesEnum.NUCLEO_ADMIN in user.roles else None,
    )

    serializer = SeasonSummarySerializer(season)
    return Response(serializer.data)


urlpatterns = [
    path("", SeasonListCreateView.as_view(), name="season-list-create"),
    path("current/", get_current_season_view, name="current-season"),
    path("<int:season_id>/summary/", get_season_summary_view, name="season-summary"),
]
