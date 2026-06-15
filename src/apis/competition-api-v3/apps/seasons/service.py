from uuid import UUID

from django.db import transaction
from django.utils import timezone
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import SeasonCreatedV1
from taca_events.pydantic_schemas.seasons import SeasonCreatedData

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

    # emit event to OutboxTable
    emit_schema_event(
        event=SeasonCreatedV1(
            data=SeasonCreatedData(season_id=season.id, name=season.name)
        ),
        aggregate_id=season.id,
    )

    return season


@transaction.atomic
def create_initial_season(name: str):
    """
    Create the initial season if it doesn't exist.
    This function is intended to be called during the application startup.
    """
    if Season.objects.exists():
        return

    # create the initial season
    season = Season.objects.create(name=name, is_current=True)

    # emit event to OutboxTable
    emit_schema_event(
        event=SeasonCreatedV1(
            data=SeasonCreatedData(season_id=season.id, name=season.name)
        ),
        aggregate_id=season.id,
    )

    return
