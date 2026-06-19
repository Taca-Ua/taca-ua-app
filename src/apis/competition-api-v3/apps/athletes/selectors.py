from uuid import UUID

from django.db.models import QuerySet

from .models import Athlete


def get_athletes_table(
    admin_id: UUID = None,
    course_id: UUID = None,
    athlete_id: UUID = None,
    nucleus_id: UUID = None,
    team_id: UUID = None,
) -> QuerySet[Athlete]:
    queryset = Athlete.objects.all()

    if admin_id:
        queryset = queryset.filter(course__nucleus__admins__id=admin_id).distinct()

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if athlete_id:
        queryset = queryset.filter(id=athlete_id)

    if team_id:
        queryset = queryset.filter(teams__id=team_id)

    if nucleus_id:
        queryset = queryset.filter(course__nucleus_id=nucleus_id)

    queryset = queryset.select_related("course")
    return queryset


def get_athlete_by_id(athlete_id: UUID) -> Athlete:

    athlete_qs = get_athletes_table().filter(id=athlete_id)

    return athlete_qs.get()
