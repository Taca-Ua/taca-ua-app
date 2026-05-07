from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..logger import logger
from ..models import ModalityType, Season, SeasonModality, Team
from ..schemas import SeasonCreate, SeasonResponse
from ..utils import get_active_season

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


@router.post(
    "/seasons", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED
)
def create_season(season_payload: SeasonCreate, db: Session = Depends(get_db_session)):
    """
    Create a new season with the provided details.
    """
    try:
        # Update the current active season to inactive if it exists
        current_season = get_active_season(db)
        current_season.finished_at = datetime.now(timezone.utc)
        current_season.finished_by = season_payload.admin_id
        db.flush()  # Flush to save the changes to the current season

        # Create new season instance
        new_season = Season(
            name=season_payload.name, created_by=season_payload.admin_id
        )
        db.add(new_season)
        db.flush()  # Flush to get the new season ID

        # Copy current ModalityTypes and Teams from the most recent season if it exists
        modality_types_to_map = {}
        for modality_type in current_season.season_modality_types:
            new_modality_type = ModalityType(
                name=modality_type.name,
                description=modality_type.description,
                escaloes=modality_type.escaloes,
                is_playoff=modality_type.is_playoff,
                tournament_competitor_type=modality_type.tournament_competitor_type,
                season_id=new_season.id,
                created_by=season_payload.admin_id,
            )
            db.add(new_modality_type)
            db.flush()  # Flush to get the new modality type ID
            modality_types_to_map[modality_type.id] = new_modality_type.id
        db.flush()  # Flush to save the new modality types
        for team in current_season.season_teams:
            new_team = Team(
                modality_id=team.modality_id,
                course_id=team.course_id,
                name=team.name,
                season_id=new_season.id,
                created_by=season_payload.admin_id,
                derived_from_team_id=team.id,  # Track lineage of teams across seasons
            )
            db.add(new_team)
        db.flush()  # Flush to save the new teams

        # Create an entry associating Modalities and Courses with the new season
        for modality in current_season.season_modalities:
            new_season_modality = SeasonModality(
                season_id=new_season.id,
                modality_id=modality.modality_id,
                modality_type_id=modality_types_to_map.get(
                    modality.modality_type_id
                ),  # Map old modality type ID to new one
            )
            db.add(new_season_modality)
        db.flush()  # Flush to save the new season modalities

        for course in current_season.season_courses:
            new_season.season_courses.append(course)
        db.flush()  # Flush to save the new season courses

        db.commit()
        return new_season.to_dict()

    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Season with the same name already exists",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/seasons/current", response_model=SeasonResponse)
def get_current_season_route(db: Session = Depends(get_db_session)):
    """
    Retrieve the current active season with its associated modalities and modality types.
    """
    try:
        current_season = get_active_season(db)
        if not current_season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No active season found"
            )
        return current_season.to_dict()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
