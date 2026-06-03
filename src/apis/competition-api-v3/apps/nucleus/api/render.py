from django.db import models
from django.db.models import QuerySet

from ..models import Nucleus


def render_nucleus_list(nucleos: QuerySet[Nucleus]) -> QuerySet[Nucleus]:
    """Render a queryset of nucleos to the API response format."""

    # current implementation is simple as there are no complex relationships to render
    # but this function can be expanded in the future if needed
    return nucleos


def render_nucleus_detail(nucleo: QuerySet[Nucleus] | Nucleus) -> QuerySet[Nucleus]:
    """Render a single nucleus to the API response format."""

    # pass from a single instance to a queryset for consistent rendering logic
    if isinstance(nucleo, Nucleus):
        nucleo = Nucleus.objects.filter(id=nucleo.id)

    nucleo = render_nucleus_list(nucleo)

    # current implementation is simple as there are no complex relationships to render
    # but this function can be expanded in the future if needed

    return nucleo
