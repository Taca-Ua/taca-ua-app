from uuid import UUID

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import QuerySet

from .models import Nucleus


def get_nucleus_table(
    nucleus_id: UUID = None, *, context_season_id: int = None
) -> QuerySet[Nucleus]:
    """Returns a queryset of all Nucleus instances."""
    queryset = Nucleus.objects.all()

    if nucleus_id is not None:
        queryset = queryset.filter(id=nucleus_id)

    if context_season_id is not None:
        queryset = queryset.annotate(
            belongs_to_season=models.Exists(
                Nucleus.seasons.through.objects.filter(
                    nucleus_id=models.OuterRef("id"), season_id=context_season_id
                )
            )
        )

    return queryset


def get_nucleus_by_id(nucleus_id: UUID, *, context_season_id: int = None) -> Nucleus:
    """Returns the Nucleus instance with the given ID."""
    nucleus_qs = get_nucleus_table(nucleus_id, context_season_id=context_season_id)

    nucleus_qs = nucleus_qs.annotate(
        relevant_season_ids=ArrayAgg("seasons__id", distinct=True)
    )

    return nucleus_qs.get()
