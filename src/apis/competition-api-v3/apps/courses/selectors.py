from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, OuterRef, QuerySet

from .models import Course


def get_courses_table(*, season_id: int = None) -> QuerySet[Course]:
    queryset = Course.objects.select_related("nucleus")

    # if season_id is provided, annotate courses with whether they belong to that season
    if season_id is not None:
        queryset = queryset.annotate(
            belongs_to_season=Exists(
                Course.seasons.through.objects.filter(
                    course_id=OuterRef("pk"),
                    season_id=season_id,
                )
            )
        )

    return queryset


def get_course_by_id(course_id: str, *, season_id: int = None) -> Course:

    course = get_courses_table(season_id=season_id).filter(id=course_id)

    course = course.annotate(relevant_season_ids=ArrayAgg("seasons__id", distinct=True))

    return course.get()
