from typing import Optional
from uuid import UUID

from apps.seasons.service import get_current_season
from django.db import transaction

from .models import ModalityType


@transaction.atomic
def create_modality_type(
    name: str,
    mode: str,
    tournament_competitor_type: str,
    description: Optional[str] = None,
    season_id: Optional[int] = None,
    escaloes_data: Optional[list[dict]] = None,
) -> ModalityType:
    """Create a new modality type.

    Args:
        name (str): The name of the modality type.
        description (Optional[str]): A description of the modality type.
        mode (str): The mode of the modality type.
        tournament_competitor_type (str): The type of tournament competitor.
        season_id (Optional[int]): The ID of the season.
        escaloes_data (Optional[list]): A list of escaloes data, where each item is a dict with keys 'name', 'min_participants', 'max_participants', and 'points'.

    Returns:
        ModalityType: The created modality type.
    """

    if season_id is None:
        current_season = get_current_season()
        if current_season is None:
            raise ValueError(
                "No current season found. A season must be active to create a modality type."
            )
        season_id = current_season.id

    modality_type = ModalityType.objects.create(
        name=name,
        description=description,
        mode=mode,
        tournament_competitor_type=tournament_competitor_type,
        season_id=season_id,
    )
    modality_type.save()

    if escaloes_data:
        for escaloes_item in escaloes_data:
            modality_type.escaloes.create(
                name=escaloes_item["name"],
                min_participants=escaloes_item["min_participants"],
                max_participants=escaloes_item["max_participants"],
                points=escaloes_item.get("points", []),
            )
    modality_type.save()

    return modality_type


@transaction.atomic
def update_modality_type(
    modality_type_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    mode: Optional[str] = None,
    tournament_competitor_type: Optional[str] = None,
) -> Optional[ModalityType]:
    """Update an existing modality type.

    Args:
        modality_type_id (UUID): The ID of the modality type to update.
        name (Optional[str]): The new name of the modality type.
        description (Optional[str]): The new description of the modality type.
        mode (Optional[str]): The new mode of the modality type.
        tournament_competitor_type (Optional[str]): The new tournament competitor type.

    Returns:
        Optional[ModalityType]: The updated modality type if found, otherwise None.
    """
    modality_type = ModalityType.objects.get(id=modality_type_id)
    if not modality_type:
        raise ValueError(f"Modality type with ID {modality_type_id} does not exist.")

    if name is not None:
        modality_type.name = name
    if description is not None:
        modality_type.description = description
    if mode is not None:
        modality_type.mode = mode
    if tournament_competitor_type is not None:
        modality_type.tournament_competitor_type = tournament_competitor_type

    modality_type.save()
    return modality_type


@transaction.atomic
def delete_modality_type(modality_type_id: UUID) -> bool:
    """Delete a modality type by its ID.

    Args:
        modality_type_id (UUID): The ID of the modality type to delete.

    Returns:
        bool: True if the modality type was deleted, False if it was not found.
    """

    modality_type = ModalityType.objects.get(id=modality_type_id)
    if not modality_type:
        return False

    modality_type.delete()
    return True
