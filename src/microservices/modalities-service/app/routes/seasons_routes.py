from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..logger import logger
from ..models import Season
from ..schemas import SeasonResponse

router = APIRouter()


@router.get("/seasons", response_model=List[SeasonResponse])
def get_seasons(db: Session = Depends(get_db_session)):
    """
    Retrieve all seasons with their associated modalities and modality types.
    """
    try:
        seasons = db.query(Season).all()
        return [s.to_dict() for s in seasons]
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
