from apps.courses.models import Course
from django.db import transaction
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import (
    StudentCreatedV1,
    StudentDeletedV1,
    StudentUpdatedV1,
)
from taca_events.pydantic_schemas.students import (
    StudentCreatedData,
    StudentDeletedData,
    StudentUpdatedData,
)

from .models import Athlete


@transaction.atomic
def create_athlete(name: str, student_number: str, course_id: str) -> Athlete:
    athlete = Athlete.objects.create(
        name=name, student_number=student_number, course_id=course_id
    )

    # emit event to OutboxTable
    emit_schema_event(
        event=StudentCreatedV1.create(
            aggregate_id=athlete.id,
            data=StudentCreatedData(
                student_id=str(athlete.id),
                full_name=athlete.name,
                student_number=athlete.student_number,
                course_id=athlete.course.id,
            ),
        ),
        aggregate_id=athlete.id,
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

    event_changes_made = False
    if name is not None:
        event_changes_made = True
        athlete.name = name
    if student_number is not None:
        event_changes_made = True
        athlete.student_number = student_number
    if course_id is not None:
        course = Course.objects.get(id=course_id)
        event_changes_made = True
        athlete.course = course
    if is_member is not None:
        athlete.is_member = is_member

    athlete.save()

    # emit event to OutboxTable
    if event_changes_made:
        emit_schema_event(
            event=StudentUpdatedV1.create(
                aggregate_id=athlete.id,
                data=StudentUpdatedData(
                    student_id=athlete.id,
                    full_name=athlete.name,
                    student_number=athlete.student_number,
                    course_id=athlete.course.id,
                ),
            ),
            aggregate_id=athlete.id,
        )

    return athlete


@transaction.atomic
def delete_athlete(athlete_id: str) -> None:
    athlete = Athlete.objects.get(id=athlete_id)

    # emit event to OutboxTable
    emit_schema_event(
        event=StudentDeletedV1.create(
            aggregate_id=athlete.id,
            data=StudentDeletedData(
                student_id=athlete.id,
            ),
        ),
        aggregate_id=athlete.id,
    )

    # delete the athlete after emitting the event
    athlete.delete()


@transaction.atomic
def sync_athletes_membership_status(athlete_numbers: list[str]) -> None:
    """Update the membership status of athletes based on their student numbers."""

    # set all athletes to not members first
    Athlete.objects.update(is_member=False)

    # then set the specified athletes to members
    Athlete.objects.filter(student_number__in=athlete_numbers).update(is_member=True)
