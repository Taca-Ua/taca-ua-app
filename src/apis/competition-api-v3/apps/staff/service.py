from django.db import transaction

from .models import Staff


@transaction.atomic
def create_staff(name: str, staff_number: str = None, contact: str = None) -> Staff:
    """Service to create a new staff member."""
    staff = Staff(name=name, staff_number=staff_number, contact=contact)
    staff.full_clean()  # validate the model fields
    staff.save()
    return staff


@transaction.atomic
def update_staff(
    staff_id: str, name: str = None, staff_number: str = None, contact: str = None
) -> Staff:
    """Service to update an existing staff member."""
    staff = Staff.objects.get(id=staff_id)

    if name is not None:
        staff.name = name
    if staff_number is not None:
        staff.staff_number = staff_number
    if contact is not None:
        staff.contact = contact

    staff.full_clean()  # validate the model fields
    staff.save()
    return staff


@transaction.atomic
def delete_staff(staff_id: str) -> None:
    """Service to delete a staff member."""
    staff = Staff.objects.get(id=staff_id)
    staff.delete()
