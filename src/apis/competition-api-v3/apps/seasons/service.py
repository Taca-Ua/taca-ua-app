from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .models import Season


@transaction.atomic
def create_season(name: str, admin_id: UUID) -> Season:
    assert name, "Season name is required"
    assert admin_id, "Admin ID is required"
    assert isinstance(name, str), "Season name must be a string"
    assert isinstance(admin_id, UUID), "Admin ID must be a valid UUID"

    # finish current season if exists
    current_season = get_current_season()
    if current_season:
        current_season.is_current = False
        current_season.finished_at = timezone.now()
        current_season.finished_by = str(admin_id)
        current_season.save()

    season = Season.objects.create(name=name, is_current=True)

    return season


def get_current_season() -> Season | None:
    return Season.objects.filter(is_current=True).first()
