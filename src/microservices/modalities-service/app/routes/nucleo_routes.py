from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.modalities import (
    NucleoCreatedData,
    NucleoCreatedV1,
    NucleoDeletedData,
    NucleoDeletedV1,
    NucleoUpdatedData,
    NucleoUpdatedV1,
)

from ..database import get_db_session
from ..logger import logger
from ..models import Nucleo
from ..outbox_publisher import outbox_publisher
from ..schemas import NucleoCreate, NucleoResponse, NucleoUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/nucleos", response_model=List[NucleoResponse])
def list_nucleos(db: Session = Depends(get_db_session)):
    """List all nucleos"""
    nucleos = db.query(Nucleo).all()
    return [nucleo.to_dict() for nucleo in nucleos]


@router.post(
    "/nucleos", response_model=NucleoResponse, status_code=status.HTTP_201_CREATED
)
def create_nucleo(nucleo_data: NucleoCreate, db: Session = Depends(get_db_session)):
    """Create a new nucleo"""
    try:
        nucleo = Nucleo(
            name=nucleo_data.name,
            abbreviation=nucleo_data.abbreviation,
            logo_url=nucleo_data.logo_url,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(nucleo)
        db.flush()  # Get the ID without committing

        # Emit event via outbox
        event = NucleoCreatedV1.create(
            aggregate_id=nucleo.id,
            data=NucleoCreatedData(
                nucleo_id=nucleo.id,
                name=nucleo.name,
                abbreviation=nucleo.abbreviation,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="nucleo",
            aggregate_id=nucleo.id,
            data=event.to_data_dict(),
        )

        db.commit()
        db.refresh(nucleo)
        logger.info(
            "entity_created",
            entity_type="nucleo",
            entity_id=str(nucleo.id),
            name=nucleo.name,
        )
        return nucleo.to_dict()
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "integrity_error",
            entity_type="nucleo",
            error="duplicate_abbreviation",
            details=str(e),
        )
        raise HTTPException(
            status_code=400, detail="Nucleo with this abbreviation already exists"
        )


@router.get("/nucleos/{nucleo_id}", response_model=NucleoResponse)
def get_nucleo(nucleo_id: UUID, db: Session = Depends(get_db_session)):
    """Get a nucleo by ID"""
    nucleo = db.query(Nucleo).filter(Nucleo.id == nucleo_id).first()
    if not nucleo:
        logger.warning(
            "entity_not_found", entity_type="nucleo", entity_id=str(nucleo_id)
        )
        raise HTTPException(status_code=404, detail="Nucleo not found")
    return nucleo.to_dict()


@router.put("/nucleos/{nucleo_id}", response_model=NucleoResponse)
def update_nucleo(
    nucleo_id: UUID, nucleo_data: NucleoUpdate, db: Session = Depends(get_db_session)
):
    """Update a nucleo"""
    nucleo = db.query(Nucleo).filter(Nucleo.id == nucleo_id).first()
    if not nucleo:
        raise HTTPException(status_code=404, detail="Nucleo not found")

    changes_made = {}
    if nucleo_data.name is not None:
        nucleo.name = nucleo_data.name
        changes_made["name"] = nucleo_data.name
    if nucleo_data.abbreviation is not None:
        nucleo.abbreviation = nucleo_data.abbreviation
        changes_made["abbreviation"] = nucleo_data.abbreviation
    if nucleo_data.logo_url is not None:
        nucleo.logo_url = nucleo_data.logo_url
    nucleo.updated_at = datetime.now(timezone.utc)

    try:
        # Emit event via outbox
        event = NucleoUpdatedV1.create(
            aggregate_id=nucleo.id,
            data=NucleoUpdatedData(
                nucleo_id=nucleo.id,
                name=changes_made.get("name"),
                abbreviation=changes_made.get("abbreviation"),
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="nucleo",
            aggregate_id=nucleo.id,
            data=event.to_data_dict(),
        )

        db.commit()
        db.refresh(nucleo)
        logger.info(f"Updated nucleo: {nucleo.id}")
        return nucleo.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Nucleo with this abbreviation already exists"
        )


@router.delete("/nucleos/{nucleo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nucleo(nucleo_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a nucleo"""
    nucleo = db.query(Nucleo).filter(Nucleo.id == nucleo_id).first()
    if not nucleo:
        raise HTTPException(status_code=404, detail="Nucleo not found")

    # Emit event via outbox before deleting
    event = NucleoDeletedV1.create(
        aggregate_id=nucleo.id,
        data=NucleoDeletedData(
            nucleo_id=nucleo.id,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="nucleo",
        aggregate_id=nucleo.id,
        data=event.to_data_dict(),
    )

    db.delete(nucleo)
    db.commit()
    logger.info(f"Deleted nucleo: {nucleo_id}")


@router.get("/nucleos/admin/{admin_id}", response_model=List[NucleoResponse])
def list_nucleos_by_admin(admin_id: UUID, db: Session = Depends(get_db_session)):
    """List all nucleos associated with a specific admin user ID"""
    str_admin_id = str(admin_id)
    nucleos = db.query(Nucleo).filter(Nucleo.admins_ids.contains([str_admin_id])).all()
    print(f"Found {len(nucleos)} nucleos for admin {admin_id}")
    return [nucleo.to_dict() for nucleo in nucleos]


@router.put(
    "/nucleos/admin/{admin_id}/associate/",
    status_code=status.HTTP_200_OK,
)
def associate_admin_with_nucleos(
    admin_id: UUID,
    nucleo_ids: List[UUID],
    db: Session = Depends(get_db_session),
):
    """Remove previous associations and associate an admin user with multiple nucleos"""
    # First, remove the admin ID from all nucleos that currently have it
    str_admin_id = str(admin_id)
    db.query(Nucleo).filter(Nucleo.admins_ids.contains([str_admin_id])).update(
        {Nucleo.admins_ids: func.array_remove(Nucleo.admins_ids, str_admin_id)},
        synchronize_session=False,
    )

    # Then, add the admin ID to the specified nucleos
    str_nucleo_ids = [str(nucleo_id) for nucleo_id in nucleo_ids]
    db.query(Nucleo).filter(Nucleo.id.in_(str_nucleo_ids)).update(
        {Nucleo.admins_ids: func.array_append(Nucleo.admins_ids, str_admin_id)},
        synchronize_session=False,
    )

    db.commit()
    return {"message": "Admin associations updated successfully"}


@router.post("/nucleos/batch-admin", response_model=Dict[str, List[NucleoResponse]])
def list_nucleos_by_batch_admin_ids(
    admin_ids: List[UUID], db: Session = Depends(get_db_session)
):
    """List all nucleos associated with a batch of admin user IDs"""
    str_admin_ids = [str(admin_id) for admin_id in admin_ids]
    nucleos = db.query(Nucleo).filter(Nucleo.admins_ids.overlap(str_admin_ids)).all()

    # return a dictionary mapping admin ID to a list of associated nucleos
    resp = {str(admin_id): [] for admin_id in admin_ids}
    str_admin_ids = set(str_admin_ids)  # Convert to set for faster lookup
    for nucleo in nucleos:
        for admin_id in nucleo.admins_ids:
            if admin_id in str_admin_ids:
                resp[admin_id].append(nucleo.to_dict())
    return resp
