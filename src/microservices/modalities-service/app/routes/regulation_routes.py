import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.modalities import (
    RegulationCreatedData,
    RegulationCreatedV1,
    RegulationDeletedData,
    RegulationDeletedV1,
    RegulationUpdatedData,
    RegulationUpdatedV1,
)

from ..database import get_db_session
from ..models import Regulation
from ..outbox_publisher import outbox_publisher
from ..schemas import (
    RegulationInternalCreate,
    RegulationInternalUpdate,
    RegulationResponse,
)
from ..utils import get_active_season

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/regulations", tags=["Regulations"])


@router.post(
    "/internal", response_model=RegulationResponse, status_code=status.HTTP_201_CREATED
)
def create_regulation_internal(
    payload: RegulationInternalCreate, db: Session = Depends(get_db_session)
):
    # If season_id is not provided, associate with active season
    relevant_season_id = payload.season_id
    if relevant_season_id is None:
        relevant_season_id = get_active_season(db).id

    try:
        new_reg = Regulation(
            title=payload.title,
            description=payload.description,
            file_url=payload.file_url,
            season_id=relevant_season_id,
        )
        db.add(new_reg)
        db.flush()  # Get ID before commit for event emission

        event = RegulationCreatedV1.create(
            aggregate_id=new_reg.id,
            data=RegulationCreatedData(
                regulation_id=new_reg.id,
                title=new_reg.title,
                description=new_reg.description,
                file_url=new_reg.file_url,
                season_id=new_reg.season_id,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type=event.aggregate_type(),
            aggregate_id=new_reg.id,
            data=event.to_data_dict(),
        )

        db.commit()
        db.refresh(new_reg)

        logger.info(f"Regulamento '{new_reg.title}' criado com ID {new_reg.id}")
        return new_reg.to_dict()

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao persistir: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar.")


@router.get("", response_model=List[RegulationResponse])
def list_regulations(
    season_id: Optional[int] = None, db: Session = Depends(get_db_session)
):
    regulations = db.query(Regulation)

    if season_id is not None:
        regulations = regulations.filter(Regulation.season_id == season_id)

    regulations = regulations.all()
    return [reg.to_dict() for reg in regulations]


@router.get("/{regulation_id}", response_model=RegulationResponse)
def get_regulation(regulation_id: UUID, db: Session = Depends(get_db_session)):
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulamento não encontrado")
    return regulation.to_dict()


@router.put("/{regulation_id}", response_model=RegulationResponse)
def update_regulation(
    regulation_id: UUID,
    payload: RegulationInternalUpdate,
    db: Session = Depends(get_db_session),
):
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulamento não encontrado")

    try:
        if payload.title is not None:
            regulation.title = payload.title
        if payload.description is not None:
            regulation.description = payload.description
        db.flush()

        event = RegulationUpdatedV1.create(
            aggregate_id=regulation.id,
            data=RegulationUpdatedData(
                regulation_id=regulation.id,
                title=regulation.title,
                description=regulation.description,
                file_url=regulation.file_url,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type=event.aggregate_type(),
            aggregate_id=regulation.id,
            data=event.to_data_dict(),
        )
        db.commit()

        db.refresh(regulation)
        return regulation.to_dict()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar.")


@router.delete("/{regulation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_regulation(regulation_id: UUID, db: Session = Depends(get_db_session)):
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulamento não encontrado")

    try:

        event = RegulationDeletedV1.create(
            aggregate_id=regulation.id,
            data=RegulationDeletedData(
                regulation_id=regulation.id,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type=event.aggregate_type(),
            aggregate_id=regulation.id,
            data=event.to_data_dict(),
        )

        db.delete(regulation)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao remover.")
