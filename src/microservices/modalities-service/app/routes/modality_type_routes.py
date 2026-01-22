from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..logger import logger
from ..models import ModalityType
from ..schemas import ModalityTypeCreate, ModalityTypeResponse, ModalityTypeUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/modality-types", response_model=List[ModalityTypeResponse])
def list_modality_types(db: Session = Depends(get_db_session)):
    """List all modality types"""
    modality_types = db.query(ModalityType).all()
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
        modality_type = ModalityType(
            name=modality_type_data.name,
            description=modality_type_data.description,
            escaloes=modality_type_data.escaloes_encoder(),
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(modality_type)
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

    if modality_type_data.name is not None:
        modality_type.name = modality_type_data.name
    if modality_type_data.description is not None:
        modality_type.description = modality_type_data.description
    if modality_type_data.escaloes is not None:
        modality_type.escaloes = modality_type_data.escaloes_encoder()
    modality_type.updated_at = datetime.now(timezone.utc)

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

    db.delete(modality_type)
    db.commit()
    logger.info(f"Deleted modality type: {modality_type_id}")
