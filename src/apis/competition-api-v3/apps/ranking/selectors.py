from dataclasses import dataclass

from apps.courses.models import Course
from apps.modalities.models import Modality
from django.db.models import Count, Q
from django.db.models.aggregates import Sum


@dataclass
class CourseRankingEntry:
    course: Course
    points: int
    tournaments_participated: int = 0


@dataclass
class ModalityRankingBreakdownEntry:
    modality: Modality
    points: int


def get_general_ranking(season_id: int) -> list[CourseRankingEntry]:

    courses_ranking = (
        Course.objects.annotate(
            points=Sum(
                "coursetournamentposition__points",
                filter=Q(coursetournamentposition__season_id=season_id),
            ),
            tournament_count=Count(
                "coursetournamentposition__tournament_id",
                filter=Q(coursetournamentposition__season_id=season_id),
                distinct=True,
            ),
        )
        .exclude(points__isnull=True)
        .order_by("-points")
    )

    return [
        CourseRankingEntry(
            course=cr, points=cr.points, tournaments_participated=cr.tournament_count
        )
        for cr in courses_ranking
    ]


def get_modality_ranking(season_id: int, modality_id: int) -> list[CourseRankingEntry]:

    courses_ranking = (
        Course.objects.annotate(
            points=Sum(
                "coursetournamentposition__points",
                filter=Q(coursetournamentposition__season_id=season_id)
                & Q(coursetournamentposition__modality_id=modality_id),
            )
        )
        .exclude(points__isnull=True)
        .order_by("-points")
    )

    return [CourseRankingEntry(course=cr, points=cr.points) for cr in courses_ranking]


def get_modality_ranking_breakdown(
    season_id: int, course_id: int
) -> list[ModalityRankingBreakdownEntry]:

    modality_ranking = (
        Modality.objects.annotate(
            points=Sum(
                "coursetournamentposition__points",
                filter=Q(coursetournamentposition__season_id=season_id)
                & Q(coursetournamentposition__course_id=course_id),
            )
        )
        .exclude(points__isnull=True)
        .order_by("-points")
    )

    return [
        ModalityRankingBreakdownEntry(modality=mr, points=mr.points)
        for mr in modality_ranking
    ]
