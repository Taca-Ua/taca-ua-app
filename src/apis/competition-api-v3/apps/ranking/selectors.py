from uuid import UUID

from apps.courses.models import Course
from apps.courses.selectors import get_courses_table
from apps.modalities.models import Modality
from django.db.models import (
    Count,
    F,
    IntegerField,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
)
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce

from .models import RankingAmmendment


class CourseRanked(Course):
    """This is a proxy model for Course, used to represent a course with its ranking information."""

    tournament_count: int = 0
    tournament_points: int = 0
    extra_points: int = 0
    points: int

    class Meta:
        managed = False
        abstract = True


class ModalityRanked(Modality):
    """This is a proxy model for Modality, used to represent a modality with its ranking information."""

    tournament_points: int = 0
    extra_points: int = 0
    points: int

    class Meta:
        managed = False
        abstract = True


def get_ranking_table(
    season_id: int, modality_id: UUID | None = None
) -> QuerySet[CourseRanked]:

    # Calculate extra points for each course in the season
    extra_points = (
        RankingAmmendment.objects.filter(
            course=OuterRef("pk"),
            season_id=season_id,
            # if a modality_id is provided, filter by that modality; otherwise, include all modalities
            modality_id=modality_id if modality_id is not None else Q(),
        )
        .values("course")
        .annotate(total_points=Sum("points"))
        .values("total_points")
    )

    queryset = (
        get_courses_table(season_id=season_id)
        .annotate(
            tournament_count=Count(
                "coursetournamentposition__tournament_id",
                distinct=True,
            ),
            tournament_points=Sum(
                "coursetournamentposition__points",
                filter=(
                    Q(coursetournamentposition__season_id=season_id)
                    # if a modality_id is provided, filter by that modality; otherwise, include all modalities
                    & (
                        Q(coursetournamentposition__modality_id=modality_id)
                        if modality_id is not None
                        else Q()
                    )
                ),
            ),
            extra_points=Coalesce(
                Subquery(extra_points, output_field=IntegerField()),
                Value(0),
            ),
            points=Coalesce(F("tournament_points"), Value(0)) + F("extra_points"),
        )
        .exclude(points__isnull=True)
        .order_by("-points")
    )

    return queryset


def get_modality_ranking_table(
    season_id: int, course_id: UUID
) -> QuerySet[ModalityRanked]:
    # Calculate extra points for each modality in the season
    extra_points = (
        RankingAmmendment.objects.filter(
            modality=OuterRef("pk"), season_id=season_id, course_id=course_id
        )
        .values("modality")
        .annotate(total_points=Sum("points"))
        .values("total_points")
    )

    queryset = (
        Modality.objects.annotate(
            tournament_points=Sum(
                "coursetournamentposition__points",
                filter=Q(
                    coursetournamentposition__season_id=season_id,
                    coursetournamentposition__course_id=course_id,
                ),
            ),
            extra_points=Coalesce(
                Subquery(extra_points, output_field=IntegerField()),
                Value(0),
            ),
            points=Coalesce(F("tournament_points"), Value(0)) + F("extra_points"),
        )
        .exclude(points__isnull=True)
        .order_by("-points")
    )

    return queryset


def get_ammendments_for_season_table(season_id: int) -> QuerySet[RankingAmmendment]:
    queryset = (
        RankingAmmendment.objects.filter(season_id=season_id)
        .select_related("course", "modality")
        .order_by("-created_at")
    )

    return queryset
