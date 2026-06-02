from django.db.models import QuerySet

from ..models import Staff


def render_staff_list(staff: QuerySet[Staff]) -> QuerySet[Staff]:
    return staff


def render_staff_detail(staff: QuerySet[Staff] | Staff) -> QuerySet[Staff]:

    if isinstance(staff, Staff):
        staff = Staff.objects.filter(id=staff.id)

    staff = render_staff_list(staff)

    return staff
