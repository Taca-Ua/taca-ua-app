from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events import EventType

from ..database import get_db_session
from ..logger import logger
from ..models import Staff
from ..outbox_publisher import outbox_publisher
from ..schemas import StaffCreate, StaffResponse, StaffUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/staff", response_model=List[StaffResponse])
def list_staff(db: Session = Depends(get_db_session)):
    """List all staff members"""
    staff = db.query(Staff).all()
    return [s.to_dict() for s in staff]


@router.post(
    "/staff", response_model=StaffResponse, status_code=status.HTTP_201_CREATED
)
def create_staff(staff_data: StaffCreate, db: Session = Depends(get_db_session)):
    """Create a new staff member"""
    # Validate that at least one of staff_number or contact is provided
    if not staff_data.staff_number and not staff_data.contact:
        raise HTTPException(
            status_code=400,
            detail="At least one of staff_number or contact must be provided",
        )

    try:
        staff = Staff(
            full_name=staff_data.full_name,
            staff_number=staff_data.staff_number,
            contact=staff_data.contact,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(staff)
        db.flush()  # Get staff.id before commit

        # Emit staff.created event
        outbox_publisher.emit_event(
            db=db,
            event_type=EventType.STAFF_CREATED,
            aggregate_type="staff",
            aggregate_id=staff.id,
            data={
                "staff_id": str(staff.id),
                "full_name": staff.full_name,
                "staff_number": staff.staff_number,
                "contact": staff.contact,
            },
        )

        db.commit()
        db.refresh(staff)
        logger.info(f"Created staff: {staff.id}")
        return staff.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Staff with this staff number or contact already exists",
        )


@router.get("/staff/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: UUID, db: Session = Depends(get_db_session)):
    """Get a staff member by ID"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff.to_dict()


@router.put("/staff/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: UUID, staff_data: StaffUpdate, db: Session = Depends(get_db_session)
):
    """Update a staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    changes_made = {}
    if staff_data.full_name is not None:
        staff.full_name = staff_data.full_name
        changes_made["full_name"] = staff_data.full_name
    if staff_data.staff_number is not None:
        staff.staff_number = staff_data.staff_number
        changes_made["staff_number"] = staff_data.staff_number
    if staff_data.contact is not None:
        staff.contact = staff_data.contact
        changes_made["contact"] = staff_data.contact
    staff.updated_at = datetime.now(timezone.utc)

    # Emit staff.updated event
    outbox_publisher.emit_event(
        db=db,
        event_type=EventType.STAFF_UPDATED,
        aggregate_type="staff",
        aggregate_id=staff.id,
        data={
            "staff_id": str(staff.id),
            **{
                k: v
                for k, v in changes_made.items()
                if k in ["full_name", "staff_number", "contact"]
            },
        },
    )

    try:
        db.commit()
        db.refresh(staff)
        logger.info(f"Updated staff: {staff.id}")
        return staff.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Staff with this staff number or contact already exists",
        )


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    # Emit staff.deleted event
    outbox_publisher.emit_event(
        db=db,
        event_type=EventType.STAFF_DELETED,
        aggregate_type="staff",
        aggregate_id=staff.id,
        data={
            "staff_id": str(staff.id),
        },
    )

    db.delete(staff)
    db.commit()
    logger.info(f"Deleted staff: {staff_id}")
