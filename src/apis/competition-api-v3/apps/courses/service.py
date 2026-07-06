from uuid import UUID

from apps.nucleus.models import Nucleus
from apps.seasons.models import Season
from apps.seasons.selectors import get_current_season
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Course


@transaction.atomic
def create_course(name, abbreviation, nucleo_id) -> Course:

    season = get_current_season()
    if not season:
        raise ValidationError(
            "No active season found. Cannot create course without an active season."
        )

    nucleus = Nucleus.objects.get(id=nucleo_id)
    if not nucleus:
        raise ValidationError(
            f"Nucleus with id {nucleo_id} not found. Cannot create course without a valid nucleus."
        )

    course = Course.objects.create(
        name=name,
        abbreviation=abbreviation,
        nucleus=nucleus,
    )
    course.seasons.add(season)
    course.save()

    return course


@transaction.atomic
def update_course(course_id, name=None, abbreviation=None, nucleo_id=None) -> Course:
    course = Course.objects.get(id=course_id)
    if not course:
        raise ValidationError(
            f"Course with id {course_id} not found. Cannot update non-existent course."
        )

    if name is not None or course.name != name:
        course.name = name

    if abbreviation is not None or course.abbreviation != abbreviation:
        course.abbreviation = abbreviation

    if nucleo_id is not None or (
        course.nucleus and str(course.nucleus.id) != str(nucleo_id)
    ):
        nucleus = Nucleus.objects.get(id=nucleo_id)

        if not nucleus:
            raise ValidationError(
                f"Nucleus with id {nucleo_id} not found. Cannot update course with invalid nucleus."
            )

        course.nucleus = nucleus

    course.save()

    return course


@transaction.atomic
def delete_course(course_id) -> None:
    course = Course.objects.get(id=course_id)
    if not course:
        raise ValidationError(
            f"Course with id {course_id} not found. Cannot delete non-existent course."
        )

    course.delete()


@transaction.atomic
def add_course_to_season(course_id: UUID, season_id: int) -> Course:
    season = Season.objects.get(id=season_id)
    if not season:
        raise ValidationError(
            f"Season with id {season_id} not found. Cannot add course to non-existent season."
        )

    course = Course.objects.get(id=course_id)
    if not course:
        raise ValidationError(
            f"Course with id {course_id} not found. Cannot add non-existent course to season."
        )

    course.seasons.add(season)
    course.save()

    return course


@transaction.atomic
def remove_course_from_season(course_id, season_id) -> Course:
    season = Season.objects.get(id=season_id)
    if not season:
        raise ValidationError(
            f"Season with id {season_id} not found. Cannot remove course from non-existent season."
        )

    course = Course.objects.get(id=course_id)
    if not course:
        raise ValidationError(
            f"Course with id {course_id} not found. Cannot remove non-existent course from season."
        )

    course.seasons.remove(season)
    course.save()

    return course
