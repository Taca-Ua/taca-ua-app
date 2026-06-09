from uuid import UUID

from django.db.models import QuerySet

from .models import Regulation


def get_regulations_table() -> QuerySet[Regulation]:
    return Regulation.objects.all()


def get_regulation_by_id(regulation_id: UUID) -> Regulation:
    regulation_qs = get_regulations_table()
    return regulation_qs.get(id=regulation_id)
