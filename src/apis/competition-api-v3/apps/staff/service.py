from django.db import transaction
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import StaffCreatedV1, StaffDeletedV1, StaffUpdatedV1
from taca_events.pydantic_schemas.staff import (
    StaffCreatedData,
    StaffDeletedData,
    StaffUpdatedData,
)

from .models import Staff


@transaction.atomic
def create_staff(name: str, staff_number: str = None, contact: str = None) -> Staff:
    """Service to create a new staff member."""
    staff = Staff(name=name, staff_number=staff_number, contact=contact)
    staff.full_clean()  # validate the model fields
    staff.save()

    # emit event to OutboxTable
    emit_schema_event(
        event=StaffCreatedV1(
            data=StaffCreatedData(
                staff_id=staff.id,
                full_name=staff.name,
                staff_number=staff.staff_number,
                contact=staff.contact,
            )
        ),
        aggregate_id=staff.id,
    )
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

    # emit event to OutboxTable
    emit_schema_event(
        event=StaffUpdatedV1(
            data=StaffUpdatedData(
                staff_id=staff.id,
                full_name=staff.name,
                staff_number=staff.staff_number,
                contact=staff.contact,
            )
        ),
        aggregate_id=staff.id,
    )

    return staff


@transaction.atomic
def delete_staff(staff_id: str) -> None:
    """Service to delete a staff member."""
    staff = Staff.objects.get(id=staff_id)

    # emit event to OutboxTable
    emit_schema_event(
        event=StaffDeletedV1(
            data=StaffDeletedData(
                staff_id=staff.id,
            )
        ),
        aggregate_id=staff.id,
    )

    staff.delete()
