from uuid import UUID

from django.db.models import QuerySet

from .models import Athlete


def get_athletes_table() -> QuerySet[Athlete]:
    return Athlete.objects.select_related("course").all()


def get_athlete_by_id(athlete_id: UUID) -> Athlete:

    athlete_qs = get_athletes_table().filter(id=athlete_id)

    return athlete_qs.get()
