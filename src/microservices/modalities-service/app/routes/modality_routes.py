from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.modalities import (
    ModalityCreatedData,
    ModalityCreatedV1,
    ModalityDeletedData,
    ModalityDeletedV1,
    ModalityUpdatedData,
    ModalityUpdatedV1,
)

from ..database import get_db_session
from ..logger import logger
from ..models import Modality, ModalityType, Regulation, Season, SeasonModality, Team
from ..outbox_publisher import outbox_publisher
from ..schemas import (
    ModalityCreate,
    ModalityRemoveFromSeason,
    ModalityResponse,
    ModalityUpdate,
    ModalityUpdateRegulationSerializer,
)
from ..utils import get_active_season

router = APIRouter()

# Default user ID for operations (replace with actual auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"


@router.get("/modalities", response_model=List[ModalityResponse])
def list_modalities(season_id: int = None, db: Session = Depends(get_db_session)):
    """List all modalities"""
    stmt = select(Modality)

    relevant_season = None
    if season_id is not None:
        relevant_season = db.query(Season).filter(Season.id == season_id).first()
        if not relevant_season:
            raise HTTPException(status_code=404, detail="Season not found")
    else:
        relevant_season = get_active_season(db)

    modalities = db.execute(stmt).scalars().unique().all()
    return [modality.to_dict(relevant_season.id) for modality in modalities]


@router.post(
    "/modalities", response_model=ModalityResponse, status_code=status.HTTP_201_CREATED
)
def create_modality(
    modality_data: ModalityCreate, db: Session = Depends(get_db_session)
):
    """Create a new modality"""
    active_season = get_active_season(db)

    # Validate modality type exists
    if modality_data.modality_type_id not in [
        mt.id for mt in active_season.season_modality_types
    ]:
        raise HTTPException(
            status_code=404, detail="Modality type not found for active season"
        )
    modality_type = (
        db.query(ModalityType)
        .filter(ModalityType.id == modality_data.modality_type_id)
        .filter(ModalityType.season_id == active_season.id)
        .first()
    )
    if not modality_type:
        raise HTTPException(
            status_code=404, detail="Modality type not found for active season"
        )

    try:
        modality = Modality(
            name=modality_data.name,
            created_by=DEFAULT_USER_ID,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(modality)
        db.flush()  # To get modality.id before commit

        # Associate modality with active season
        season_modality = SeasonModality(
            season_id=active_season.id,
            modality_id=modality.id,
            modality_type_id=modality_type.id,
        )
        db.add(season_modality)
        db.flush()

        # Emit event via outbox
        event = ModalityCreatedV1.create(
            aggregate_id=modality.id,
            data=ModalityCreatedData(
                modality_id=modality.id,
                modality_type_id=modality_type.id,
                name=modality.name,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="modality",
            aggregate_id=modality.id,
            data=event.to_data_dict(),
        )

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
def get_modality(
    modality_id: UUID, season_id: int = None, db: Session = Depends(get_db_session)
):
    """Get a modality by ID"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    relevant_season = None
    if season_id is not None:
        relevant_season = db.query(Season).filter(Season.id == season_id).first()
        if not relevant_season:
            raise HTTPException(status_code=404, detail="Season not found")
    else:
        relevant_season = get_active_season(db)

    return modality.to_dict(relevant_season.id)


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

    changes_made = {}
    if modality_data.name is not None:
        modality.name = modality_data.name
        changes_made["name"] = modality_data.name
    if modality_data.modality_type_id is not None:
        if modality_data.season_id is None:
            raise HTTPException(
                status_code=400,
                detail="season_id is required when updating modality_type_id",
            )

        relevant_season = None
        if modality_data.season_id is not None:
            relevant_season = (
                db.query(Season).filter(Season.id == modality_data.season_id).first()
            )
            if not relevant_season:
                raise HTTPException(status_code=404, detail="Season not found")
        else:
            relevant_season = get_active_season(db)

        modality_type = (
            db.query(ModalityType)
            .filter(ModalityType.id == modality_data.modality_type_id)
            .filter(ModalityType.season_id == relevant_season.id)
            .first()
        )
        if not modality_type:
            raise HTTPException(
                status_code=404, detail="Modality type not found for active season"
            )

        sm_relationship = (
            db.query(SeasonModality)
            .filter(
                SeasonModality.modality_id == modality_id,
                SeasonModality.season_id == relevant_season.id,
            )
            .first()
        )

        if not sm_relationship:
            sm_relationship = SeasonModality(
                season_id=relevant_season.id,
                modality_id=modality_id,
                modality_type_id=modality_type.id,
            )
            db.add(sm_relationship)
        else:
            sm_relationship.modality_type_id = modality_type.id
        db.flush()
        changes_made["modality_type_id"] = str(modality_type.id)
    modality.updated_at = datetime.now(timezone.utc)

    # Emit event via outbox
    event = ModalityUpdatedV1.create(
        aggregate_id=modality.id,
        data=ModalityUpdatedData(
            modality_id=modality.id,
            name=changes_made.get("name"),
            modality_type_id=changes_made.get("modality_type_id"),
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="modality",
        aggregate_id=modality.id,
        data=event.to_data_dict(),
    )

    try:
        db.commit()
        db.refresh(modality)
        logger.info(f"Updated modality: {modality.id}")
        return modality.to_dict(season_id=modality_data.season_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Modality with this name already exists"
        )


@router.put(
    "/modalities/{modality_id}/remove-from-season", response_model=ModalityResponse
)
def remove_modality_from_season(
    modality_id: UUID,
    modality_data: ModalityRemoveFromSeason,
    db: Session = Depends(get_db_session),
):
    """Remove a modality from a season"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    season_modality = (
        db.query(SeasonModality)
        .filter(
            SeasonModality.modality_id == modality_id,
            SeasonModality.season_id == modality_data.season_id,
        )
        .first()
    )
    if not season_modality:
        raise HTTPException(
            status_code=404,
            detail="Modality is not associated with the specified season",
        )

    # Check if modality there are teams associated with this modality in the season
    teams = db.query(Team).filter(
        Team.modality_id == modality_id, Team.season_id == modality_data.season_id
    )
    if teams.count() > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove modality from season because there are teams associated with it",
        )

    db.delete(season_modality)

    # Emit event via outbox
    event = ModalityUpdatedV1.create(
        aggregate_id=modality.id,
        data=ModalityUpdatedData(
            modality_id=modality.id,
            modality_type_id=None,  # Indicate removal of modality type association
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="modality",
        aggregate_id=modality.id,
        data=event.to_data_dict(),
    )

    db.commit()
    logger.info(f"Removed modality {modality_id} from season {modality_data.season_id}")
    return modality.to_dict(season_id=modality_data.season_id)


@router.delete("/modalities/{modality_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_modality(modality_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a modality"""
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    # Emit event via outbox
    event = ModalityDeletedV1.create(
        aggregate_id=modality.id,
        data=ModalityDeletedData(
            modality_id=modality.id,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="modality",
        aggregate_id=modality.id,
        data=event.to_data_dict(),
    )

    active_season = get_active_season(db)
    db.query(SeasonModality).filter(
        SeasonModality.modality_id == modality_id,
        SeasonModality.season_id == active_season.id,
    ).delete()

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


@router.put(
    "/modalities/{modality_id}/update-regulation", response_model=ModalityResponse
)
def update_modality_regulation(
    modality_id: UUID,
    modality_data: ModalityUpdateRegulationSerializer,
    db: Session = Depends(get_db_session),
):
    """Update a modality's regulation for a specific season"""
    season_id = modality_data.season_id
    regulation_id = modality_data.regulation_id

    # Validate modality exists
    modality = db.query(Modality).filter(Modality.id == modality_id).first()
    if not modality:
        raise HTTPException(status_code=404, detail="Modality not found")

    # Validate modality is associated with the season
    season_modality = (
        db.query(SeasonModality)
        .filter(
            SeasonModality.modality_id == modality_id,
            SeasonModality.season_id == season_id,
        )
        .first()
    )
    if not season_modality:
        raise HTTPException(
            status_code=404,
            detail="Modality is not associated with the specified season",
        )

    # Validate regulation exists for the season
    if regulation_id is not None:
        regulation = (
            db.query(Regulation)
            .filter(Regulation.id == regulation_id, Regulation.season_id == season_id)
            .first()
        )
        if not regulation:
            raise HTTPException(
                status_code=404, detail="Regulation not found for the specified season"
            )

    # Update regulation association
    season_modality.regulation_id = (
        regulation_id  # if regulation_id is None, this will remove the association
    )
    modality.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(modality)

    logger.info(
        f"Updated regulation for modality {modality_id} in season {season_id} to regulation {regulation_id}"
    )
    return modality.to_dict(season_id=season_id)
