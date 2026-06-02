from typing import Optional
from uuid import UUID

from apps.seasons.service import get_current_season
from django.db.models import QuerySet

from .models import ModalityType


def list_modality_types(
    season_id: Optional[int] = None, mode: Optional[str] = None
) -> QuerySet[ModalityType]:
    """Retrieve a list of all modality types.

    Args:
        season_id (Optional[int]): The ID of the season to filter modality types. If None, it will try to get the current season.
        mode (Optional[str]): The mode to filter modality types. If None, it will not filter by mode.

    Returns:
        QuerySet[ModalityType]: A queryset of modality types matching the criteria.
    """

    # If season_id is not provided, try to get the current season and use its ID
    if season_id is None:
        season = get_current_season()
        season_id = season.id if season else None

    queryset = ModalityType.objects.all()
    if season_id is not None:
        queryset = queryset.filter(season_id=season_id)

    if mode is not None:
        queryset = queryset.filter(mode=mode)

    return queryset.order_by("name")


def get_modality_type(modality_type_id: UUID) -> QuerySet[ModalityType]:
    """Retrieve a modality type by its ID.

    Args:
        modality_type_id (UUID): The ID of the modality type.

    Returns:
        QuerySet[ModalityType]: A queryset containing the modality type if found, otherwise an empty queryset.
    """
    modality_type = ModalityType.objects.filter(id=modality_type_id)

    if not modality_type.exists():
        raise ValueError(f"Modality type with ID {modality_type_id} does not exist.")

    return modality_type
