from django.db.models import QuerySet

from .models import Nucleus


def list_nucleus() -> QuerySet[Nucleus]:
    """Returns a queryset of all Nucleus instances."""
    return Nucleus.objects.all()


def get_nucleus(nucleus_id: str) -> QuerySet[Nucleus]:
    """Returns a queryset of the Nucleus instance with the given ID."""

    queryset = Nucleus.objects.filter(id=nucleus_id)

    # check if the queryset is empty and raise an error if it is
    if not queryset.exists():
        raise ValueError(f"Nucleus with ID {nucleus_id} does not exist.")

    return queryset
