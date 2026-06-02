from django.db.models import QuerySet

from .models import Athlete


def list_athletes() -> QuerySet[Athlete]:
    return Athlete.objects.all()


def get_athlete(athlete_id: str) -> QuerySet[Athlete]:

    queryset = Athlete.objects.filter(id=athlete_id)
    if not queryset.exists():
        raise Athlete.DoesNotExist(f"Athlete with id {athlete_id} does not exist.")

    return queryset
