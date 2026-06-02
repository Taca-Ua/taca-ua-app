"""This module contains the functions that convert the models to the API responses."""

from django.db.models import QuerySet

from ..models import ModalityType


def render_modality_types(
    modality_types: QuerySet[ModalityType],
) -> QuerySet[ModalityType]:
    """Render a queryset of modality types to the API response format."""

    # current implementation is simple as there are no complex relationships to render
    # but this function can be expanded in the future if needed

    return modality_types


def render_modality_type(
    modality_type: QuerySet[ModalityType] | ModalityType,
) -> QuerySet[ModalityType]:
    """Render a single modality type queryset to the API response format."""

    if isinstance(modality_type, ModalityType):
        modality_type = ModalityType.objects.filter(id=modality_type.id)

    modality_type = render_modality_types(modality_type)

    # current implementation is simple as there are no complex relationships to render
    # but this function can be expanded in the future if needed

    return modality_type
