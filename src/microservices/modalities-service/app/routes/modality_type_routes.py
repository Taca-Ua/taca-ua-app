from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.modalities import (
    ModalityTypeCreatedData,
    ModalityTypeCreatedV1,
    ModalityTypeDeletedData,
    ModalityTypeDeletedV1,
    ModalityTypeUpdatedData,
    ModalityTypeUpdatedV1,
    _EscalaoData,
)

from ..database import get_db_session
from ..logger import logger
from ..models import ModalityType
from ..outbox_publisher import outbox_publisher
from ..schemas import ModalityTypeCreate, ModalityTypeResponse, ModalityTypeUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/modality-types", response_model=List[ModalityTypeResponse])
def list_modality_types(
    exclude_playoff: bool = False, db: Session = Depends(get_db_session)
):
    """List all modality types"""
    query = db.query(ModalityType)
    if exclude_playoff:
        query = query.filter(ModalityType.is_playoff == False)  # noqa: E712
    modality_types = query.all()
    return [mt.to_dict() for mt in modality_types]


@router.post(
    "/modality-types",
    response_model=ModalityTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_modality_type(
    modality_type_data: ModalityTypeCreate, db: Session = Depends(get_db_session)
):
    """Create a new modality type"""
    try:
        # Check if a playoff type already exists
        if modality_type_data.is_playoff:
            existing_playoff = (
                db.query(ModalityType).filter(ModalityType.is_playoff).first()
            )
            if existing_playoff:
                raise HTTPException(
                    status_code=400,
                    detail="A playoff modality type already exists",
                )

        modality_type = ModalityType(
            name=modality_type_data.name,
            description=modality_type_data.description,
            escaloes=modality_type_data.escaloes_encoder(),
            is_playoff=modality_type_data.is_playoff,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(modality_type)
        db.flush()  # To get the ID before commit

        # Emit modality type created event
        event = ModalityTypeCreatedV1.create(
            aggregate_id=modality_type.id,
            data=ModalityTypeCreatedData(
                modality_type_id=modality_type.id,
                name=modality_type.name,
                description=modality_type.description,
                escaloes=[
                    _EscalaoData(
                        min_participants=e.minParticipants,
                        max_participants=e.maxParticipants,
                        points=e.points,
                    )
                    for e in modality_type_data.escaloes
                ],
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="modality_type",
            aggregate_id=modality_type.id,
            data=event.to_data_dict(),
        )

        db.commit()
        db.refresh(modality_type)
        logger.info(f"Created modality type: {modality_type.id}")
        return modality_type.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality type with this name already exists"
        )


@router.get("/modality-types/{modality_type_id}", response_model=ModalityTypeResponse)
def get_modality_type(modality_type_id: UUID, db: Session = Depends(get_db_session)):
    """Get a modality type by ID"""
    modality_type = (
        db.query(ModalityType).filter(ModalityType.id == modality_type_id).first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")
    return modality_type.to_dict()


@router.get("/playoff-modality-type", response_model=ModalityTypeResponse)
def get_playoff_modality_type(db: Session = Depends(get_db_session)):
    """Get the modality type used for playoff tournaments"""
    modality_type = db.query(ModalityType).filter(ModalityType.is_playoff).first()
    if not modality_type:
        raise HTTPException(status_code=404, detail="Playoff modality type not found")
    return modality_type.to_dict()


@router.put("/modality-types/{modality_type_id}", response_model=ModalityTypeResponse)
def update_modality_type(
    modality_type_id: UUID,
    modality_type_data: ModalityTypeUpdate,
    db: Session = Depends(get_db_session),
):
    """Update a modality type"""
    modality_type = (
        db.query(ModalityType).filter(ModalityType.id == modality_type_id).first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")

    changes_made = {}
    if modality_type_data.name is not None:
        modality_type.name = modality_type_data.name
        changes_made["name"] = modality_type_data.name
    if modality_type_data.description is not None:
        modality_type.description = modality_type_data.description
        changes_made["description"] = modality_type_data.description
    if modality_type_data.escaloes is not None:
        modality_type.escaloes = modality_type_data.escaloes_encoder()
        changes_made["escaloes"] = [i.to_dict() for i in modality_type_data.escaloes]
    if modality_type_data.is_playoff is not None:
        if modality_type_data.is_playoff and not modality_type.is_playoff:
            # If trying to set this modality type as playoff, check if another playoff type already exists
            existing_playoff = (
                db.query(ModalityType)
                .filter(ModalityType.is_playoff, ModalityType.id != modality_type_id)
                .first()
            )
            if existing_playoff:
                raise HTTPException(
                    status_code=400,
                    detail="Another playoff modality type already exists",
                )
        modality_type.is_playoff = modality_type_data.is_playoff
        changes_made["is_playoff"] = modality_type_data.is_playoff
    modality_type.updated_at = datetime.now(timezone.utc)

    # Emit modality type updated event
    event = ModalityTypeUpdatedV1.create(
        aggregate_id=modality_type.id,
        data=ModalityTypeUpdatedData(
            modality_type_id=modality_type.id,
            name=changes_made.get("name"),
            description=changes_made.get("description"),
            escaloes=[
                _EscalaoData(
                    min_participants=e.minParticipants,
                    max_participants=e.maxParticipants,
                    points=e.points,
                )
                for e in modality_type_data.escaloes
            ],
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="modality_type",
        aggregate_id=modality_type.id,
        data=event.to_data_dict(),
    )

    try:
        db.commit()
        db.refresh(modality_type)
        logger.info(f"Updated modality type: {modality_type.id}")
        return modality_type.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality type with this name already exists"
        )


@router.delete(
    "/modality-types/{modality_type_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_modality_type(modality_type_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a modality type"""
    modality_type = (
        db.query(ModalityType).filter(ModalityType.id == modality_type_id).first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")

    # Emit modality type deleted event
    event = ModalityTypeDeletedV1.create(
        aggregate_id=modality_type.id,
        data=ModalityTypeDeletedData(modality_type_id=modality_type.id),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="modality_type",
        aggregate_id=modality_type.id,
        data=event.to_data_dict(),
    )

    db.delete(modality_type)
    db.commit()
    logger.info(f"Deleted modality type: {modality_type_id}")
