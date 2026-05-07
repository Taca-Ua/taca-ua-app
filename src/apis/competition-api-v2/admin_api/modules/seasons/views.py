"""
Season management views
"""

from admin_api.utils.decorators import (
    RoleRequiredMixin,
    require_auth,
    require_roles_class_method,
)
from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SeasonCreateSerializer, SeasonListSerializer
from .service import seasons_service


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
        seasons = seasons_service.list_seasons()

        serializer = SeasonListSerializer(seasons, many=True)
        return Response(serializer.data)

    @require_roles_class_method("general_admin")
    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        season = seasons_service.create_season(
            name=serializer.validated_data["name"], admin_id=request.user_id
        )

        serializer = SeasonListSerializer(season)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    responses=SeasonListSerializer,
    description="Get the current active season",
    tags=["Season Management"],
)
@api_view(["GET"])
@require_auth
def current_season(request):
    season = seasons_service.get_current_season()
    if not season:
        return Response(
            {"detail": "No active season found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = SeasonListSerializer(season)
    return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("", SeasonListCreateView.as_view(), name="season-list"),
    path("current/", current_season, name="season-current"),
]
