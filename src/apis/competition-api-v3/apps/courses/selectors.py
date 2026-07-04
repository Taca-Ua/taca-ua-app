from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, OuterRef, QuerySet

from .models import Course


def get_courses_table(
    season_id: int = None,
    admin_id: str = None,
    nucleo_id: str = None,
    *,
    context_season_id: int = None,
    context_admin_id: str = None
) -> QuerySet[Course]:
    queryset = Course.objects.all()

    if season_id is not None:
        queryset = queryset.filter(seasons__id=season_id)

    if nucleo_id is not None:
        queryset = queryset.filter(nucleus__id=nucleo_id)

    if admin_id is not None:
        queryset = queryset.filter(nucleus__admins__id=admin_id).distinct()

    queryset = queryset.select_related("nucleus")

    if context_season_id is not None:
        # if context_season_id is provided, annotate courses with whether they belong to that season
        queryset = queryset.annotate(
            belongs_to_season=Exists(
                Course.seasons.through.objects.filter(
                    course_id=OuterRef("pk"),
                    season_id=context_season_id,
                )
            )
        )

    return queryset


def get_course_by_id(course_id: str, *, context_season_id: int = None) -> Course:

    course = get_courses_table(context_season_id=context_season_id).filter(id=course_id)

    course = course.annotate(relevant_season_ids=ArrayAgg("seasons__id", distinct=True))

    return course.get()
