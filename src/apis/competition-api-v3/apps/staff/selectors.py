from uuid import UUID

from django.db.models import QuerySet

from .models import Staff


def get_staff_table() -> QuerySet[Staff]:
    return Staff.objects.all()


def get_staff_by_id(staff_id: UUID) -> Staff:
    staff_qs = get_staff_table().filter(id=staff_id)
    return staff_qs.get()
