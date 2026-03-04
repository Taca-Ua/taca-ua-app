"""
API routes for Tournaments Service.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from taca_events import EventType

from .database import get_db_session
from .event_helpers import emit_event
from .logger import logger
from .models import (
    CompetitorType,
    Tournament,
    TournamentCompetitor,
    TournamentRankingPosition,
)
from .schemas import (
    CompetitorInput,
    TournamentCreate,
    TournamentFinish,
    TournamentResponse,
    TournamentUpdate,
)

router = APIRouter()


# ==================== Helpers ====================
def add_competitor(db: Session, tournament_id: UUID, competitor_input: CompetitorInput):
    """Add a competitor to a tournament.

    Args:
        db (Session): Database session
        tournament_id (UUID): ID of the tournament
        competitor_input (CompetitorInput): Competitor details

    Returns:
        None
    """

    competitor_type = (
        CompetitorType.TEAM
        if competitor_input.competitor_type == "team"
        else CompetitorType.ATHLETE
    )

    # Check if competitor is not already in tournament
    query = db.query(TournamentCompetitor).filter(
        TournamentCompetitor.tournament_id == tournament_id,
        TournamentCompetitor.competitor_type == competitor_type,
    )

    if competitor_type == CompetitorType.TEAM:
        query = query.filter(TournamentCompetitor.team_id == competitor_input.team_id)
    else:
        query = query.filter(
            TournamentCompetitor.athlete_id == competitor_input.athlete_id
        )

    existing = query.first()

    if existing:
        return  # Competitor already exists, skip adding

    tournament_competitor = TournamentCompetitor(
        tournament_id=tournament_id,
        competitor_type=competitor_type,
        team_id=(
            competitor_input.team_id if competitor_type == CompetitorType.TEAM else None
        ),
        athlete_id=(
            competitor_input.athlete_id
            if competitor_type == CompetitorType.ATHLETE
            else None
        ),
    )
    db.add(tournament_competitor)
    db.flush()

    # Emit event for added competitor
    emit_event(
        db=db,
        event_type=EventType.TOURNAMENT_COMPETITOR_ADDED,
        aggregate_type="tournament_competitor",
        aggregate_id=str(tournament_competitor.id),
        data={
            "tournament_id": str(tournament_id),
            "competitor_type": competitor_input.competitor_type,
            "competitor_entity_id": str(
                competitor_input.team_id or competitor_input.athlete_id
            ),
        },
    )


# ==================== Tournament Endpoints ====================


@router.get("/tournaments", response_model=List[TournamentResponse])
async def list_tournaments(
    status_filter: str = None,
    modality_id: UUID = None,
    db: Session = Depends(get_db_session),
):
    """List all tournaments with optional filters"""
    query = db.query(Tournament)

    if status_filter:
        query = query.filter(Tournament.status == status_filter)
    if modality_id:
        query = query.filter(Tournament.modality_id == modality_id)

    tournaments = query.all()
    return [TournamentResponse(**t.to_dict(include_ranking=True)) for t in tournaments]


@router.get("/tournaments/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: UUID, db: Session = Depends(get_db_session)):
    """Get a tournament by ID"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    return TournamentResponse(**tournament.to_dict(include_ranking=True))


@router.post(
    "/tournaments",
    response_model=TournamentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tournament(
    data: TournamentCreate, db: Session = Depends(get_db_session)
):
    """Create a new tournament"""
    try:
        # Create tournament
        tournament = Tournament(
            modality_id=data.modality_id,
            name=data.name,
            start_date=data.start_date,
            status="draft",
            created_by=data.created_by,
        )
        db.add(tournament)
        db.flush()  # Get the ID before committing

        # Emit event for tournament creation
        emit_event(
            db=db,
            event_type=EventType.TOURNAMENT_CREATED,
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            data={
                "tournament_id": str(tournament.id),
                "modality_id": str(tournament.modality_id),
                "name": tournament.name,
                "start_date": tournament.start_date.isoformat(),
                "status": tournament.status,
            },
        )

        # Add competitors if provided
        if data.competitors:
            for competitor_input in data.competitors:
                add_competitor(db, tournament.id, competitor_input)

        db.commit()
        db.refresh(tournament)

        logger.info(f"Created tournament {tournament.id}: {tournament.name}")
        return TournamentResponse(**tournament.to_dict(include_ranking=True))

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating tournament: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating tournament: {str(e)}",
        )


@router.put("/tournaments/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: UUID, data: TournamentUpdate, db: Session = Depends(get_db_session)
):
    """Update a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    # Update fields
    changes_made = {}
    if data.name is not None:
        tournament.name = data.name
        changes_made["name"] = data.name
    if data.start_date is not None:
        tournament.start_date = data.start_date
        changes_made["start_date"] = data.start_date.isoformat()
    if data.status is not None:
        tournament.status = data.status
        changes_made["status"] = data.status

    tournament.updated_at = datetime.now(timezone.utc)

    # Create outbox event
    emit_event(
        db=db,
        event_type=EventType.TOURNAMENT_UPDATED,
        aggregate_type="tournament",
        aggregate_id=str(tournament.id),
        data={
            "tournament_id": str(tournament.id),
            **{
                k: v
                for k, v in changes_made.items()
                if k in ["name", "start_date", "status"]
            },
        },
    )

    try:
        db.commit()
        db.refresh(tournament)
        logger.info(f"Updated tournament {tournament.id}")
        return TournamentResponse(**tournament.to_dict(include_ranking=True))
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating tournament: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating tournament: {str(e)}",
        )


@router.delete("/tournaments/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(tournament_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        # Emit event before deleting
        emit_event(
            db=db,
            event_type=EventType.TOURNAMENT_DELETED,
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            data={"tournament_id": str(tournament.id)},
        )

        db.delete(tournament)
        db.commit()

        logger.info(f"Deleted tournament {tournament_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting tournament: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting tournament: {str(e)}",
        )


@router.post("/tournaments/{tournament_id}/finish", response_model=TournamentResponse)
async def finish_tournament(
    tournament_id: UUID, data: TournamentFinish, db: Session = Depends(get_db_session)
):
    """Mark a tournament as finished and set final rankings"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    if tournament.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament is already finished",
        )

    try:
        # Delete existing ranking positions
        db.query(TournamentRankingPosition).filter(
            TournamentRankingPosition.tournament_id == tournament_id
        ).delete()

        # Create new ranking positions
        for entry in data.ranking_entries:
            ranking_position = TournamentRankingPosition(
                tournament_id=tournament_id,
                team_id=entry.team_id,
                position=entry.position,
            )
            db.add(ranking_position)

        # Update tournament status
        tournament.status = "finished"
        tournament.finished_at = datetime.now(timezone.utc)
        tournament.finished_by = data.finished_by
        tournament.updated_at = datetime.now(timezone.utc)

        # Create outbox event
        emit_event(
            db=db,
            event_type=EventType.TOURNAMENT_FINISHED,
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            data={
                "tournament_id": str(tournament.id),
                "ranking_entries": [
                    {"team_id": str(entry.team_id), "position": entry.position}
                    for entry in data.ranking_entries
                ],
            },
        )

        db.commit()
        db.refresh(tournament)

        logger.info(f"Finished tournament {tournament.id}")
        return TournamentResponse(**tournament.to_dict(include_ranking=True))

    except Exception as e:
        db.rollback()
        logger.error(f"Error finishing tournament: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finishing tournament: {str(e)}",
        )


@router.put(
    "/tournaments/{tournament_id}/competitors/add", response_model=TournamentResponse
)
async def add_competitors_to_tournament(
    tournament_id: UUID,
    competitors: List[CompetitorInput],
    db: Session = Depends(get_db_session),
):
    """Add competitors to a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        for competitor_input in competitors:
            add_competitor(db, tournament_id, competitor_input)

        db.commit()
        logger.info(f"Added competitors to tournament {tournament_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding competitors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding competitors: {str(e)}",
        )

    return TournamentResponse(**tournament.to_dict(include_ranking=True))


@router.put(
    "/tournaments/{tournament_id}/competitors/remove", response_model=TournamentResponse
)
async def remove_competitors_from_tournament(
    tournament_id: UUID,
    competitor_ids: List[UUID],
    db: Session = Depends(get_db_session),
):
    """Remove competitors from a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        for competitor_id in competitor_ids:
            db.query(TournamentCompetitor).filter(
                TournamentCompetitor.tournament_id == tournament_id,
                TournamentCompetitor.id == competitor_id,
            ).delete()
            db.flush()

            # Emit event for removed competitor
            emit_event(
                db=db,
                event_type=EventType.TOURNAMENT_COMPETITOR_DELETED,
                aggregate_type="tournament_competitor",
                aggregate_id=str(competitor_id),
                data={
                    "competitor_id": str(competitor_id),
                    "tournament_id": str(tournament_id),
                },
            )

        db.commit()
        logger.info(f"Removed competitors from tournament {tournament_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing competitors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing competitors: {str(e)}",
        )

    return TournamentResponse(**tournament.to_dict(include_ranking=True))


# ==================== Health Check ====================


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tournaments-service"}
