import logging
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..models import Regulation
from ..schemas import RegulationInternalCreate, RegulationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/regulations", tags=["Regulations"])

@router.post("/internal", response_model=RegulationResponse, status_code=status.HTTP_201_CREATED)
def create_regulation_internal(
    payload: RegulationInternalCreate, 
    db: Session = Depends(get_db_session)
):
    try:
        new_reg = Regulation(
            title=payload.title,
            description=payload.description,
            file_url=payload.file_url
        )
        
        db.add(new_reg)
        db.commit()
        db.refresh(new_reg)
        
        logger.info(f"Regulamento '{new_reg.title}' criado com ID {new_reg.id}")
        return new_reg.to_dict()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao persistir: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar.")

@router.get("", response_model=List[RegulationResponse])
def list_regulations(db: Session = Depends(get_db_session)):
    regulations = db.query(Regulation).all()
    return [reg.to_dict() for reg in regulations]

@router.get("/{regulation_id}", response_model=RegulationResponse)
def get_regulation(regulation_id: UUID, db: Session = Depends(get_db_session)):
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulamento não encontrado")
    return regulation.to_dict()

@router.delete("/{regulation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_regulation(regulation_id: UUID, db: Session = Depends(get_db_session)):
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(status_code=404, detail="Regulamento não encontrado")
    
    try:
        db.delete(regulation)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao remover.")