from django.db.models import QuerySet

from .models import Season


def get_seasons_table() -> QuerySet[Season]:
    return Season.objects.all()


def get_season_by_id(season_id: int) -> Season:
    season_qs = get_seasons_table()
    return season_qs.get(id=season_id)


def get_current_season() -> Season:
    season_qs = get_seasons_table()

    current_season = season_qs.filter(is_current=True)

    if not current_season.exists():
        raise Season.DoesNotExist("No current season found.")
    if current_season.count() > 1:
        raise Season.MultipleObjectsReturned("Multiple current seasons found.")

    return current_season.get()
