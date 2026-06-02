from django.db.models import QuerySet

from .models import Staff


def list_staff() -> QuerySet[Staff]:
    """Query to list all staff members."""
    return Staff.objects.all()


def get_staff(staff_id: str) -> QuerySet[Staff]:
    """Query to get a specific staff member by ID."""
    queryset = Staff.objects.filter(id=staff_id)
    if not queryset.exists():
        raise Staff.DoesNotExist(f"Staff member with id {staff_id} does not exist.")

    return queryset
