from uuid import UUID

from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from shared.auth.decorators import require_auth

from ..selectors import (
    get_general_ranking,
    get_modality_ranking,
    get_modality_ranking_breakdown,
)
from .filters import RankingSeasonFilterSerializer
from .serializers import (
    CourseRankingBreakdownEntrySerializer,
    GeneralRankingEntrySerializer,
    ModalityRankingEntrySerializer,
)


@extend_schema(
    summary="General Ranking",
    description="Retrieve the general ranking for a specific season",
    tags=["Ranking"],
    parameters=[RankingSeasonFilterSerializer],
    responses={200: GeneralRankingEntrySerializer(many=True)},
)
@api_view(["GET"])
@require_auth
def general_ranking(request: Request):
    serializer = RankingSeasonFilterSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    general_ranking = get_general_ranking(
        season_id=serializer.validated_data.get("season_id")
    )

    serializer = GeneralRankingEntrySerializer(general_ranking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Modality Ranking",
    description="Retrieve the ranking for a specific modality and season",
    tags=["Ranking"],
    parameters=[RankingSeasonFilterSerializer],
    responses={200: ModalityRankingEntrySerializer(many=True)},
)
@api_view(["GET"])
@require_auth
def modality_ranking(request: Request, modality_id: UUID):
    serializer = RankingSeasonFilterSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    modality_ranking = get_modality_ranking(
        season_id=serializer.validated_data.get("season_id"), modality_id=modality_id
    )

    serializer = ModalityRankingEntrySerializer(modality_ranking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Course Ranking",
    description="Retrieve the ranking of a course",
    tags=["Ranking"],
    parameters=[RankingSeasonFilterSerializer],
    responses={200: CourseRankingBreakdownEntrySerializer(many=True)},
)
@api_view(["GET"])
@require_auth
def course_ranking(request: Request, course_id: UUID):
    serializer = RankingSeasonFilterSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    course_ranking = get_modality_ranking_breakdown(
        season_id=serializer.validated_data.get("season_id"), course_id=course_id
    )

    serializer = CourseRankingBreakdownEntrySerializer(course_ranking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


urlpatterns = [
    path("general/", general_ranking, name="general-ranking"),
    path("modality/<uuid:modality_id>/", modality_ranking, name="modality-ranking"),
    path("course/<uuid:course_id>/", course_ranking, name="course-ranking"),
]
