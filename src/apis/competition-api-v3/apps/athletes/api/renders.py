from django.db.models import QuerySet

from ..models import Athlete


def render_athletes(athletes: QuerySet[Athlete]) -> QuerySet[Athlete]:
    return athletes


def render_athlete(athlete: QuerySet[Athlete] | Athlete) -> QuerySet[Athlete]:
    if isinstance(athlete, Athlete):
        athlete = Athlete.objects.filter(id=athlete.id)

    athlete = render_athletes(athlete)

    return athlete
