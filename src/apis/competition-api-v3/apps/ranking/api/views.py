from uuid import UUID

from django.urls import path
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.auth.decorators import RoleRequiredMixin, require_auth, require_roles
from shared.auth.utils import RolesEnum

from ..selectors import (
    get_ammendments_for_season_table,
    get_modality_ranking_table,
    get_ranking_table,
)
from ..service import create_ammendment, recompute_rankings
from .filters import ModalityFilterSerializer
from .serializers import (
    CourseModalityBreakdownRankingEntrySerializer,
    RankingAmmendmentCreateSerializer,
    RankingAmmendmentSerializer,
    RankingEntrySerializer,
)


@extend_schema(
    summary="General Ranking",
    description="Retrieve the general ranking for a specific season",
    tags=["Ranking"],
    parameters=[ModalityFilterSerializer],
    responses={200: RankingEntrySerializer(many=True)},
)
@api_view(["GET"])
@require_auth
def general_ranking(request: Request, season_id: int):
    serializer = ModalityFilterSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    general_ranking = get_ranking_table(
        season_id=season_id,
        modality_id=serializer.validated_data.get("modality_id"),
    )

    serializer = RankingEntrySerializer(general_ranking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Course Ranking",
    description="Retrieve the ranking of a course",
    tags=["Ranking"],
    responses={200: CourseModalityBreakdownRankingEntrySerializer(many=True)},
)
@api_view(["GET"])
@require_auth
def course_ranking(request: Request, season_id: int, course_id: UUID):

    course_ranking = get_modality_ranking_table(
        season_id=season_id, course_id=course_id
    )

    serializer = CourseModalityBreakdownRankingEntrySerializer(
        course_ranking, many=True
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Recompute Rankings",
    description="Recompute the rankings for all tournaments in a specific season",
    tags=["Ranking"],
    responses={200: "Rankings recomputed."},
)
@api_view(["POST"])
@require_roles(RolesEnum.GENERAL_ADMIN)
def recompute_rankings_view(request: Request, season_id: int):

    recompute_rankings(season_id=season_id)

    return Response({"message": "Rankings recomputed."}, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve ammendments for a specific season",
        description="Retrieve ammendments for a specific season",
        tags=["Ranking"],
        responses={200: RankingAmmendmentSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Add ammendment to the ranking",
        description="Add ammendment to the ranking for a specific season",
        tags=["Ranking"],
        request=RankingAmmendmentCreateSerializer,
        responses={200: RankingAmmendmentSerializer},
    ),
)
class RankingAmmendmentView(APIView, RoleRequiredMixin):

    def get(self, request: Request, season_id: int):

        ammendments = get_ammendments_for_season_table(season_id=season_id)

        serializer = RankingAmmendmentSerializer(ammendments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, season_id: int):
        serializer = RankingAmmendmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ammendment = create_ammendment(
            season_id=season_id,
            course_id=serializer.validated_data.get("course_id"),
            modality_id=serializer.validated_data.get("modality_id"),
            points=serializer.validated_data.get("points"),
            reason=serializer.validated_data.get("reason"),
        )

        serializer = RankingAmmendmentSerializer(ammendment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


urlpatterns = [
    path("season/<int:season_id>/", general_ranking, name="general-ranking"),
    path(
        "season/<int:season_id>/course/<uuid:course_id>/",
        course_ranking,
        name="course-ranking",
    ),
    path(
        "season/<int:season_id>/recompute/",
        recompute_rankings_view,
        name="recompute-rankings",
    ),
    path(
        "season/<int:season_id>/ammendments/",
        RankingAmmendmentView.as_view(),
        name="ranking-ammendments",
    ),
]
