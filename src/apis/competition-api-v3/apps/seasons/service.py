from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .models import Season
from .selectors import get_current_season


@transaction.atomic
def create_season(name: str, admin_id: UUID) -> Season:

    # finish current season
    current_season = get_current_season()
    current_season.is_current = False
    current_season.finished_at = timezone.now()
    current_season.finished_by = str(admin_id)
    current_season.save()

    # create new season
    season = Season.objects.create(name=name, is_current=True)

    return season
