from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, OuterRef, QuerySet

from ..models import Course


def render_courses(
    courses: QuerySet[Course], season_id: int | None = None
) -> QuerySet[Course]:

    # inject related data to avoid n+1 queries when serializing
    courses = courses.select_related("nucleus")

    # annotate if course belongs to season (if season_id is provided)
    if season_id is not None:
        courses = courses.annotate(
            belongs_to_season=Exists(
                Course.seasons.through.objects.filter(
                    course_id=OuterRef("pk"),
                    season_id=season_id,
                )
            )
        )

    return courses


def render_course(
    course: QuerySet[Course] | Course, season_id: int | None = None
) -> QuerySet[Course]:

    if isinstance(course, Course):
        course = Course.objects.filter(id=course.id)

    course = render_courses(course, season_id)

    course = course.annotate(relevant_season_ids=ArrayAgg("seasons__id", distinct=True))

    return course
