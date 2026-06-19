from uuid import UUID

from django.db.models import QuerySet

from .models import Regulation


def get_regulations_table(regulation_id: UUID = None) -> QuerySet[Regulation]:
    queryset = Regulation.objects.all()
    if regulation_id is not None:
        queryset = queryset.filter(id=regulation_id)
    return queryset


def get_regulation_by_id(regulation_id: UUID) -> Regulation:
    regulation_qs = get_regulations_table().filter(id=regulation_id)
    return regulation_qs.get()
