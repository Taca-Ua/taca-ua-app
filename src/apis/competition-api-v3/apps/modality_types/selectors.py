from typing import Optional
from uuid import UUID

from apps.seasons.selectors import get_current_season
from django.db.models import QuerySet

from .models import ModalityType


def get_modality_types_table(
    season_id: Optional[int] = None, mode: Optional[str] = None
) -> QuerySet[ModalityType]:
    """Retrieve a list of all modality types.

    Args:
        season_id (Optional[int]): The ID of the season to filter modality types. If None, it will try to get the current season.
        mode (Optional[str]): The mode to filter modality types. If None, it will not filter by mode.

    Returns:
        QuerySet[ModalityType]: A queryset of modality types matching the criteria.
    """

    # if season_id is not provided, try to get the current season and use its ID
    if season_id is None:
        season = get_current_season()
        season_id = season.id if season else None

    queryset = ModalityType.objects.all()

    if season_id is not None:
        queryset = queryset.filter(season_id=season_id)

    if mode is not None:
        queryset = queryset.filter(mode=mode)

    return queryset.order_by("name")


def get_modality_type_by_id(modality_type_id: UUID) -> ModalityType:
    """Retrieve a modality type by its ID.

    Args:
        modality_type_id (UUID): The ID of the modality type.

    Returns:
        ModalityType: The modality type if found, otherwise an empty queryset.
    """
    modality_type_qs = get_modality_types_table()

    return modality_type_qs.get(id=modality_type_id)
