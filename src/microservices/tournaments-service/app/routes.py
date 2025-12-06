"""
API routes for Tournaments Service.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import schemas
from .database import get_db_session
from .events import (
    publish_tournament_created,
    publish_tournament_deleted,
    publish_tournament_finished,
    publish_tournament_updated,
)
from .models import Tournament, TournamentStatus

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
    tournament = Tournament(
        modality_id=tournament_data.modality_id,
        name=tournament_data.name,
        season_id=tournament_data.season_id,
        rules=tournament_data.rules,
        teams=tournament_data.teams,
        start_date=tournament_data.start_date,
        created_by=tournament_data.created_by,
        status=TournamentStatus.DRAFT,
    )

    db.add(tournament)
    db.commit()
    db.refresh(tournament)

    background_tasks.add_task(publish_tournament_created, tournament)
    return tournament


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
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status == TournamentStatus.FINISHED:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "TOURNAMENT_ALREADY_FINISHED",
                    "message": "Cannot update a finished tournament",
                    "details": {"tournament_id": str(tournament_id)},
                }
            },
        )

    changes = {}
    if tournament_data.name is not None:
        changes["name"] = tournament_data.name
        tournament.name = tournament_data.name
    if tournament_data.rules is not None:
        changes["rules"] = tournament_data.rules
        tournament.rules = tournament_data.rules
    if tournament_data.teams is not None:
        changes["teams"] = tournament_data.teams
        tournament.teams = tournament_data.teams
    if tournament_data.start_date is not None:
        changes["start_date"] = tournament_data.start_date
        tournament.start_date = tournament_data.start_date

    tournament.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(tournament)

    background_tasks.add_task(publish_tournament_updated, tournament, changes)
    return tournament


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
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status == TournamentStatus.FINISHED:
        raise HTTPException(
            status_code=409, detail="Cannot modify a finished tournament"
        )

    current_teams = tournament.teams or []
    new_teams = list(set(current_teams + teams_data.team_ids))
    tournament.teams = new_teams
    tournament.updated_at = datetime.now(timezone.utc)

    db.commit()

    background_tasks.add_task(publish_tournament_updated, tournament_id, teams_data)
    return {"message": "Teams added successfully", "team_count": len(new_teams)}


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
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status == TournamentStatus.FINISHED:
        raise HTTPException(
            status_code=409, detail="Cannot modify a finished tournament"
        )

    current_teams = tournament.teams or []
    new_teams = [
        team_id for team_id in current_teams if team_id not in teams_data.team_ids
    ]
    tournament.teams = new_teams
    tournament.updated_at = datetime.now(timezone.utc)

    db.commit()

    background_tasks.add_task(publish_tournament_updated, tournament_id, teams_data)
    return None


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
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status == TournamentStatus.FINISHED:
        raise HTTPException(status_code=409, detail="Tournament already finished")

    tournament.status = TournamentStatus.FINISHED
    tournament.finished_at = datetime.now(timezone.utc)
    tournament.finished_by = finish_data.finished_by
    tournament.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(tournament)

    background_tasks.add_task(publish_tournament_finished, tournament)
    return tournament


@router.get("/tournaments/{tournament_id}", response_model=schemas.TournamentResponse)
def get_tournament(
    tournament_id: UUID,
    db: Session = Depends(get_db_session),
):
    """
    Get a tournament by ID.
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return tournament


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
    query = db.query(Tournament)

    if modality_id:
        query = query.filter(Tournament.modality_id == modality_id)
    if season_id:
        query = query.filter(Tournament.season_id == season_id)
    if status:
        try:
            status_enum = TournamentStatus(status)
            query = query.filter(Tournament.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    total = query.count()
    tournaments = query.offset(offset).limit(limit).all()

    return {
        "tournaments": tournaments,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.delete("/tournaments/{tournament_id}", status_code=204)
async def delete_tournament(
    tournament_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """
    Delete a tournament.
    """
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status != TournamentStatus.DRAFT:
        raise HTTPException(
            status_code=409,
            detail="Can only delete tournaments in draft status",
        )

    # TODO: Check if there are matches associated
    # For now, we'll just delete

    db.delete(tournament)
    db.commit()

    background_tasks.add_task(publish_tournament_deleted, tournament_id)
    return None
