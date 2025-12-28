"""
Season management views
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import SeasonCreateSerializer, SeasonListSerializer


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
class SeasonListCreateView(APIView):
    def get(self, request):
        dummy_data = [
            {"id": 1, "year": 2024, "status": "finished"},
            {"id": 2, "year": 2025, "status": "active"},
            {"id": 3, "year": 2026, "status": "draft"},
        ]
        return Response(dummy_data)

    def post(self, request):
        serializer = SeasonCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dummy_response = {"id": 4, "status": "draft", **serializer.validated_data}
        return Response(dummy_response, status=status.HTTP_201_CREATED)


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Start a season",
    tags=["Season Management"],
)
@api_view(["POST"])
def season_start(request, season_id):
    dummy_response = {"id": season_id, "year": 2025, "status": "active"}
    return Response(dummy_response)


@extend_schema(
    request=None,
    responses={200: SeasonListSerializer},
    description="Finish a season",
    tags=["Season Management"],
)
@api_view(["POST"])
def season_finish(request, season_id):
    dummy_response = {"id": season_id, "year": 2025, "status": "finished"}
    return Response(dummy_response)
