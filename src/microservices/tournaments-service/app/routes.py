"""
API routes for Tournaments Service.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db_session
from .logger import logger
from .models import (
    CompetitorType,
    Tournament,
    TournamentCompetitor,
    TournamentRankingPosition,
)
from .outbox_publisher import outbox_publisher
from .schemas import (
    TournamentCreate,
    TournamentFinish,
    TournamentResponse,
    TournamentUpdate,
)

router = APIRouter()


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

        # Add competitors if provided
        if data.competitors:
            for competitor_input in data.competitors:
                competitor_type = (
                    CompetitorType.TEAM
                    if competitor_input.competitor_type == "team"
                    else CompetitorType.ATHLETE
                )

                tournament_competitor = TournamentCompetitor(
                    tournament_id=tournament.id,
                    competitor_type=competitor_type,
                    team_id=(
                        competitor_input.team_id
                        if competitor_type == CompetitorType.TEAM
                        else None
                    ),
                    athlete_id=(
                        competitor_input.athlete_id
                        if competitor_type == CompetitorType.ATHLETE
                        else None
                    ),
                )
                db.add(tournament_competitor)

        # Create outbox event
        outbox_publisher.create_event(
            db=db,
            event_type="tournament.created",
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            payload=tournament.to_dict(),
        )

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

    try:
        # Update fields
        if data.name is not None:
            tournament.name = data.name
        if data.start_date is not None:
            tournament.start_date = data.start_date
        if data.status is not None:
            tournament.status = data.status

        # Handle competitor additions
        print("Competitors to add:")
        print(data.competitors_add)
        if data.competitors_add:
            for competitor_input in data.competitors_add:
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
                    query = query.filter(
                        TournamentCompetitor.team_id == competitor_input.team_id
                    )
                else:
                    query = query.filter(
                        TournamentCompetitor.athlete_id == competitor_input.athlete_id
                    )

                existing = query.first()

                if not existing:
                    tournament_competitor = TournamentCompetitor(
                        tournament_id=tournament_id,
                        competitor_type=competitor_type,
                        team_id=(
                            competitor_input.team_id
                            if competitor_type == CompetitorType.TEAM
                            else None
                        ),
                        athlete_id=(
                            competitor_input.athlete_id
                            if competitor_type == CompetitorType.ATHLETE
                            else None
                        ),
                    )
                    db.add(tournament_competitor)

        # Handle competitor removals
        if data.competitors_remove:
            for competitor_id in data.competitors_remove:
                db.query(TournamentCompetitor).filter(
                    TournamentCompetitor.tournament_id == tournament_id,
                    TournamentCompetitor.id == competitor_id,
                ).delete()

        tournament.updated_at = datetime.now(timezone.utc)

        # Create outbox event
        outbox_publisher.create_event(
            db=db,
            event_type="tournament.updated",
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            payload=tournament.to_dict(),
        )

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
        # Create outbox event before deleting
        outbox_publisher.create_event(
            db=db,
            event_type="tournament.deleted",
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            payload={"id": str(tournament.id), "name": tournament.name},
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
        outbox_publisher.create_event(
            db=db,
            event_type="tournament.finished",
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            payload=tournament.to_dict(include_ranking=True),
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


# ==================== Health Check ====================


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tournaments-service"}
