from uuid import UUID

from django.db.models import QuerySet

from .models import Nucleus


def get_nucleus_table() -> QuerySet[Nucleus]:
    """Returns a queryset of all Nucleus instances."""
    return Nucleus.objects.all()


def get_nucleus_by_id(nucleus_id: UUID) -> Nucleus:
    """Returns the Nucleus instance with the given ID."""
    nucleus_qs = get_nucleus_table()
    return nucleus_qs.get(id=nucleus_id)
