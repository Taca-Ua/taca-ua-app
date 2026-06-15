from typing import Optional
from uuid import UUID

from apps.modality_types.models import ModalityType
from apps.seasons.selectors import get_current_season
from django.db import transaction
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import ModalityCreatedV1, ModalityUpdatedV1
from taca_events.pydantic_schemas.modalities import (
    ModalityCreatedData,
    ModalityUpdatedData,
)

from .models import Modality, SeasonModality


@transaction.atomic
def create_modality(name: str, modality_type_id: UUID) -> Modality:

    modality = Modality.objects.create(name=name)
    season = get_current_season()
    modality.modality_seasons.create(
        modality_type_id=modality_type_id, season_id=season.id
    )

    # emit event to OutboxTable
    emit_schema_event(
        event=ModalityCreatedV1(
            data=ModalityCreatedData(
                modality_id=modality.id,
                modality_type_id=modality_type_id,
                name=modality.name,
            ),
        ),
        aggregate_id=modality.id,
    )

    return modality


@transaction.atomic
def update_modality(
    modality_id: UUID,
    name: Optional[str] = None,
    modality_type_id: Optional[UUID] = None,
) -> Modality:

    modality = Modality.objects.get(id=modality_id)

    if name is not None:
        modality.name = name
        modality.save()

    if modality_type_id is not None:
        season = get_current_season()
        season_modality, created = SeasonModality.objects.get_or_create(
            modality_id=modality_id,
            season_id=season.id,
            defaults={"modality_type_id": modality_type_id},
        )
        if not created:
            season_modality.modality_type_id = modality_type_id
            season_modality.save()

    # emit event to OutboxTable
    emit_schema_event(
        event=ModalityUpdatedV1(
            data=ModalityUpdatedData(
                modality_id=modality.id,
                name=modality.name,
                modality_type_id=modality_type_id,
            ),
        ),
        aggregate_id=modality.id,
    )

    return modality


@transaction.atomic
def add_modality_to_season(
    modality_id: UUID, season_id: int, modality_type_id: UUID
) -> Modality:
    """Adds an existing modality to a season with a specific modality type"""

    # check if the modality exists
    modality = Modality.objects.filter(id=modality_id).first()
    if not modality:
        raise ValueError("Modality not found")

    # check if the modality type exists for the given season
    modality_type = ModalityType.objects.filter(
        id=modality_type_id, season__id=season_id
    ).first()
    if not modality_type:
        raise ValueError("Modality type not found for the given season")

    # create the association between modality and season with the specified modality type
    SeasonModality.objects.create(
        modality_id=modality_id, season_id=season_id, modality_type_id=modality_type_id
    )

    return modality


@transaction.atomic
def remove_modality_from_season(modality_id: UUID, season_id: int) -> Modality:
    """Removes an existing modality from a season"""

    modality = Modality.objects.filter(
        id=modality_id, modality_seasons__season_id=season_id
    ).first()

    if not modality:
        raise ValueError("Modality not found for the given season")

    SeasonModality.objects.filter(modality_id=modality_id, season_id=season_id).delete()

    return modality
