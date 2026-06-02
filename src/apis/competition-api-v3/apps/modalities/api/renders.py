"""This module contains the functions that convert the models to the API responses."""

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Exists, OuterRef, QuerySet, Subquery
from django.db.models.functions import JSONObject

from ..models import Modality, SeasonModality


def render_modalities(
    modalities: QuerySet[Modality], season_id=None
) -> QuerySet[Modality]:
    """Render the queryset of modalities to the API response format.

    Args:
        modalities (QuerySet): A queryset of Modality instances to render.
        season_id (int, optional): If provided, includes season-specific information in the response. Defaults to None.

    Returns:
        list: A list of dictionaries representing the modalities in the API response format.
    """

    if season_id:
        modalities = modalities.annotate(
            belongs_to_season=Exists(
                SeasonModality.objects.filter(
                    modality=OuterRef("pk"), season_id=season_id
                )
            )
        )

        season_modality_qs = SeasonModality.objects.filter(
            modality=OuterRef("pk"), season_id=season_id, modality_type__isnull=False
        )

        modalities = modalities.annotate(
            modality_type=Subquery(
                season_modality_qs.annotate(
                    modality_type_json=JSONObject(
                        id="modality_type__id",
                        name="modality_type__name",
                    )
                ).values("modality_type_json")[:1]
            )
        )

    return modalities


def render_modality(
    modality: QuerySet[Modality] | Modality, season_id=None
) -> QuerySet[Modality]:
    """Render a single modality queryset to the API response format.

    Args:
        modality (QuerySet[Modality] | Modality): A queryset containing a single Modality instance or a Modality instance to render.
        season_id (int, optional): If provided, includes season-specific information in the response. Defaults to None.
    """
    if isinstance(modality, Modality):
        modality = Modality.objects.filter(pk=modality.pk)

    # Reuse the render_modalities function to render a single modality
    result = render_modalities(modality, season_id=season_id)

    # Annotate the relevant seasons IDs for the modality
    result = result.annotate(
        relevant_seasons_ids=ArrayAgg("modality_seasons__season_id", distinct=True)
    )

    return result
