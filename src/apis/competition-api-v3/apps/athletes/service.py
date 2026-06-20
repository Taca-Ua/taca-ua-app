from apps.courses.models import Course
from django.db import transaction

from .models import Athlete


@transaction.atomic
def create_athlete(name: str, student_number: str, course_id: str) -> Athlete:
    athlete = Athlete.objects.create(
        name=name, student_number=student_number, course_id=course_id
    )

    return athlete


@transaction.atomic
def update_athlete(
    athlete_id: str,
    name: str = None,
    student_number: str = None,
    course_id: str = None,
    is_member: bool = None,
) -> Athlete:
    athlete = Athlete.objects.get(id=athlete_id)

    if name is not None:
        athlete.name = name
    if student_number is not None:
        athlete.student_number = student_number
    if course_id is not None:
        course = Course.objects.get(id=course_id)
        athlete.course = course
    if is_member is not None:
        athlete.is_member = is_member

    athlete.save()

    return athlete


@transaction.atomic
def delete_athlete(athlete_id: str) -> None:
    athlete = Athlete.objects.get(id=athlete_id)

    # delete the athlete after emitting the event
    athlete.delete()


@transaction.atomic
def sync_athletes_membership_status(athlete_numbers: list[str]) -> None:
    """Update the membership status of athletes based on their student numbers."""

    # set all athletes to not members first
    Athlete.objects.update(is_member=False)

    # then set the specified athletes to members
    Athlete.objects.filter(student_number__in=athlete_numbers).update(is_member=True)
