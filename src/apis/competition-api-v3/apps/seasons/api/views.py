import logging

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

from ..queries import list_seasons
from ..service import create_season, get_current_season
from .serializers import SeasonCreateSerializer, SeasonListSerializer

logger = logging.getLogger(__name__)


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
        seasons = list_seasons()

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

        logger.info(
            f"Season created by user {user.user_id}",
            extra={
                "season_id": season.id,
                "season_name": season.name,
                "admin_id": user.user_id,
            },
        )
        serializer = SeasonListSerializer(season)
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


urlpatterns = [
    path("", SeasonListCreateView.as_view(), name="season-list-create"),
    path("current/", get_current_season_view, name="current-season"),
]
