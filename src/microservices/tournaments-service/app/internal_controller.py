"""
Internal API endpoints for Tournaments Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from taca_snapshots.tournaments import (
    TournamentCompetitorSnapshotItem,
    TournamentRankingPositionSnapshotItem,
    TournamentSnapshotItem,
    TournamentsSnapshotResponse,
)

from .database import get_db_session
from .logger import logger
from .models import Tournament, TournamentCompetitor, TournamentRankingPosition

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot", response_model=TournamentsSnapshotResponse)
def get_snapshot(
    db: Session = Depends(get_db_session),
    limit: int = Query(
        default=10000,
        ge=1,
        le=50000,
        description="Maximum number of records to return per collection",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
):
    """
    Return complete snapshot of all tournaments data as strongly typed DTOs.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns all tournaments, competitors, and ranking positions.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Query Parameters:
        limit: Maximum number of records returned per collection (default 10000).
        offset: Number of records to skip (default 0).

    Returns:
        TournamentsSnapshotResponse with all tournaments domain data.
    """
    logger.info("snapshot_requested", service="tournaments", limit=limit, offset=offset)

    try:
        # Fetch domain data
        tournaments = db.query(Tournament).offset(offset).limit(limit).all()
        competitors = db.query(TournamentCompetitor).offset(offset).limit(limit).all()
        ranking_positions = (
            db.query(TournamentRankingPosition).offset(offset).limit(limit).all()
        )

        # Build typed DTOs
        tournament_dtos = [
            TournamentSnapshotItem(
                id=str(t.id),
                modality_id=str(t.modality_id),
                name=t.name,
                scoring_format_id=(
                    str(t.scoring_format_id) if t.scoring_format_id else None
                ),
                status=t.status,
                start_date=t.start_date,
                created_by=str(t.created_by),
                created_at=t.created_at,
                updated_at=t.updated_at,
                finished_at=t.finished_at,
                finished_by=str(t.finished_by) if t.finished_by else None,
            )
            for t in tournaments
        ]

        competitor_dtos = [
            TournamentCompetitorSnapshotItem(
                id=str(c.id),
                tournament_id=str(c.tournament_id),
                competitor_type=c.competitor_type.value if c.competitor_type else None,
                team_id=str(c.team_id) if c.team_id else None,
                athlete_id=str(c.athlete_id) if c.athlete_id else None,
                created_at=c.created_at,
                competitor_course_id=(
                    str(c.competitor_course_id) if c.competitor_course_id else None
                ),
            )
            for c in competitors
        ]

        ranking_position_dtos = [
            TournamentRankingPositionSnapshotItem(
                id=str(rp.id),
                tournament_id=str(rp.tournament_id),
                competitor_id=str(rp.competitor_id),
                position=rp.position,
                created_at=rp.created_at,
            )
            for rp in ranking_positions
        ]

        snapshot = TournamentsSnapshotResponse(
            tournaments=tournament_dtos,
            competitors=competitor_dtos,
            ranking_positions=ranking_position_dtos,
        )

        logger.info(
            "snapshot_generated",
            service="tournaments",
            tournaments_count=len(tournament_dtos),
            competitors_count=len(competitor_dtos),
            ranking_positions_count=len(ranking_position_dtos),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="tournaments", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "tournaments"}
