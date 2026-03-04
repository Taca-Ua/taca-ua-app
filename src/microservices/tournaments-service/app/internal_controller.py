"""
Internal API endpoints for Tournaments Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db_session
from .logger import logger
from .models import Tournament, TournamentCompetitor, TournamentRankingPosition

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db_session)):
    """
    Return complete snapshot of all tournaments data.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns all tournaments, competitors, and ranking positions.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Returns:
        JSON object with all tournaments domain data:
        - tournaments: List of all tournaments
        - competitors: List of all tournament competitors
        - ranking_positions: List of all tournament ranking positions
    """
    logger.info("snapshot_requested", service="tournaments")

    try:
        # Fetch all domain data
        tournaments = db.query(Tournament).all()
        competitors = db.query(TournamentCompetitor).all()
        ranking_positions = db.query(TournamentRankingPosition).all()

        # Convert to dictionaries
        snapshot = {
            "tournaments": [
                {
                    "id": str(t.id),
                    "modality_id": str(t.modality_id),
                    "name": t.name,
                    "status": t.status,
                    "start_date": t.start_date.isoformat() if t.start_date else None,
                    "created_by": str(t.created_by),
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                    "finished_at": t.finished_at.isoformat() if t.finished_at else None,
                    "finished_by": str(t.finished_by) if t.finished_by else None,
                }
                for t in tournaments
            ],
            "competitors": [
                {
                    "id": str(c.id),
                    "tournament_id": str(c.tournament_id),
                    "competitor_type": (
                        c.competitor_type.value if c.competitor_type else None
                    ),
                    "team_id": str(c.team_id) if c.team_id else None,
                    "athlete_id": str(c.athlete_id) if c.athlete_id else None,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in competitors
            ],
            "ranking_positions": [
                {
                    "id": str(rp.id),
                    "tournament_id": str(rp.tournament_id),
                    "competitor_id": str(rp.competitor_id),
                    "position": rp.position,
                    "created_at": rp.created_at.isoformat() if rp.created_at else None,
                }
                for rp in ranking_positions
            ],
        }

        logger.info(
            "snapshot_generated",
            service="tournaments",
            tournaments_count=len(tournaments),
            competitors_count=len(competitors),
            ranking_positions_count=len(ranking_positions),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="tournaments", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "tournaments"}
