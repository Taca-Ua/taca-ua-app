"""
API routes for Tournaments Service.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from . import schemas
from .database import get_db_session
from .events import (
    publish_tournament_created,
    publish_tournament_deleted,
    publish_tournament_finished,
    publish_tournament_updated,
)

router = APIRouter()


@router.post("/tournaments", response_model=schemas.TournamentResponse, status_code=201)
async def create_tournament(
    tournament_data: schemas.TournamentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """
    Create a new tournament.
    """

    background_tasks.add_task(publish_tournament_created, tournament_data)
    return None  # Placeholder for actual implementation


@router.put("/tournaments/{tournament_id}", response_model=schemas.TournamentResponse)
async def update_tournament(
    tournament_id: UUID,
    tournament_data: schemas.TournamentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """
    Update a tournament.
    """

    background_tasks.add_task(
        publish_tournament_updated, tournament_id, tournament_data
    )
    return None  # Placeholder for actual implementation


@router.post("/tournaments/{tournament_id}/teams")
async def add_teams_to_tournament(
    tournament_id: UUID,
    teams_data: schemas.TournamentTeamsAdd,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """
    Add teams to a tournament.
    """
    background_tasks.add_task(publish_tournament_updated, tournament_id, teams_data)
    return None  # Placeholder for actual implementation


@router.delete("/tournaments/{tournament_id}/teams", status_code=204)
async def remove_teams_from_tournament(
    tournament_id: UUID,
    teams_data: schemas.TournamentTeamsRemove,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """
    Remove teams from a tournament.
    """
    background_tasks.add_task(publish_tournament_updated, tournament_id, teams_data)
    return None  # Placeholder for actual implementation


@router.post("/tournaments/{tournament_id}/finish")
async def finish_tournament(
    tournament_id: UUID,
    finish_data: schemas.TournamentFinish,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """
    Finish a tournament.
    """
    background_tasks.add_task(publish_tournament_finished, tournament_id, finish_data)
    return None  # Placeholder for actual implementation


@router.get("/tournaments/{tournament_id}", response_model=schemas.TournamentResponse)
def get_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db_session),
):
    """
    Get a tournament by ID.
    """
    return None  # Placeholder for actual implementation


@router.get("/tournaments", response_model=schemas.TournamentListResponse)
def list_tournaments(
    modality_id: Optional[UUID] = Query(None),
    season_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
):
    """
    List tournaments with optional filters.
    """
    return None  # Placeholder for actual implementation


@router.delete("/tournaments/{tournament_id}", status_code=204)
async def delete_tournament(
    tournament_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """
    Delete a tournament.
    """
    background_tasks.add_task(publish_tournament_deleted, tournament_id)
    return None  # Placeholder for actual implementations
