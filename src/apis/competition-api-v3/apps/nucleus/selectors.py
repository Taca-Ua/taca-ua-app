from uuid import UUID

from django.db.models import QuerySet

from .models import Nucleus


def get_nucleus_table(nucleus_id: UUID = None) -> QuerySet[Nucleus]:
    """Returns a queryset of all Nucleus instances."""
    queryset = Nucleus.objects.all()

    if nucleus_id is not None:
        queryset = queryset.filter(id=nucleus_id)

    return queryset


def get_nucleus_by_id(nucleus_id: UUID) -> Nucleus:
    """Returns the Nucleus instance with the given ID."""
    nucleus_qs = get_nucleus_table().filter(id=nucleus_id)
    return nucleus_qs.get()
