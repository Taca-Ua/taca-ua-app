from django.db.models import QuerySet

from .models import Season


def list_seasons() -> QuerySet[Season]:
    """Returns a queryset of all Season instances."""
    return Season.objects.all()


def get_season(season_id: str) -> QuerySet[Season]:
    """Returns a queryset of the Season instance with the given ID."""

    queryset = Season.objects.filter(id=season_id)

    # check if the queryset is empty and raise an error if it is
    if not queryset.exists():
        raise Season.DoesNotExist(f"Season with id {season_id} does not exist.")

    return queryset
