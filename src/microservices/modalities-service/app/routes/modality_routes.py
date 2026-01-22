from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..logger import logger
from ..models import Modality, ModalityType
from ..schemas import ModalityCreate, ModalityResponse, ModalityUpdate

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/modalities", response_model=List[ModalityResponse])
def list_modalities(db: Session = Depends(get_db_session)):
    """List all modalities"""
    modalities = db.query(Modality).all()
    return [modality.to_dict() for modality in modalities]


@router.post(
    "/modalities", response_model=ModalityResponse, status_code=status.HTTP_201_CREATED
)
def create_modality(
    modality_data: ModalityCreate, db: Session = Depends(get_db_session)
):
    """Create a new modality"""
    # Validate modality type exists
    modality_type = (
        db.query(ModalityType)
        .filter(ModalityType.id == modality_data.modality_type_id)
        .first()
    )
    if not modality_type:
        raise HTTPException(status_code=404, detail="Modality type not found")

    try:
        modality = Modality(
            name=modality_data.name,
            modality_type_id=modality_data.modality_type_id,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(modality)
        db.commit()
        db.refresh(modality)
        logger.info(f"Created modality: {modality.id}")
        return modality.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality with this name already exists"
        )


@router.get("/modalities/{modality_id}", response_model=ModalityResponse)
def get_modality(modality_id: UUID, db: Session = Depends(get_db_session)):
    """Get a modality by ID"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")
    return modality.to_dict()


@router.put("/modalities/{modality_id}", response_model=ModalityResponse)
def update_modality(
    modality_id: UUID,
    modality_data: ModalityUpdate,
    db: Session = Depends(get_db_session),
):
    """Update a modality"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    if modality_data.name is not None:
        modality.name = modality_data.name
    if modality_data.modality_type_id is not None:
        modality_type = (
            db.query(ModalityType)
            .filter(ModalityType.id == modality_data.modality_type_id)
            .first()
        )
        if not modality_type:
            raise HTTPException(status_code=404, detail="Modality type not found")
        modality.modality_type_id = modality_data.modality_type_id
    modality.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(modality)
        logger.info(f"Updated modality: {modality.id}")
        return modality.to_dict()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality with this name already exists"
        )


@router.delete("/modalities/{modality_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_modality(modality_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a modality"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    db.delete(modality)
    db.commit()
    logger.info(f"Deleted modality: {modality_id}")


@router.post("/modalities/batch-get", response_model=List[ModalityResponse])
def get_modalities_by_ids(
    modality_ids: List[UUID], db: Session = Depends(get_db_session)
):
    """Get multiple modalities by their IDs"""
    modalities = db.query(Modality).filter(Modality.id.in_(modality_ids)).all()
    return [modality.to_dict() for modality in modalities]
