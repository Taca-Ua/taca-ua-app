import logging

from django.db.models import QuerySet

from .models import Modality

logger = logging.getLogger(__name__)


def list_modalities(season_id=None) -> QuerySet[Modality]:
    """Modalities list query with optional season filtering.

    Args:
        season_id (int, optional): If provided, filters modalities to those belonging to the specified season.

    Returns:
        QuerySet: A queryset of Modality instances matching the criteria.
    """

    queryset = Modality.objects.all()

    if season_id:
        queryset = queryset.filter(modality_seasons__season_id=season_id)

    return queryset


def get_modality(modality_id) -> QuerySet[Modality]:
    """Get a modality by its ID

    Args:
        modality_id (UUID): The ID of the modality to retrieve.

    Returns:
        QuerySet[Modality]: A queryset containing the matching modality.
    """

    queryset = Modality.objects.filter(id=modality_id)
    if not queryset.exists():
        raise Modality.DoesNotExist(f"Modality with id {modality_id} does not exist.")

    return queryset
