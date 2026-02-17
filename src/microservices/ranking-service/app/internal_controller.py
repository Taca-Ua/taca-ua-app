"""
Internal API endpoints for Ranking Service.

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
from .models import CourseRanking, GeneralRanking, ModalityRanking

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db_session)):
    """
    Return complete snapshot of all ranking data.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns all modality rankings, course rankings, and general rankings.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Note: Ranking data might be computed/derived, so this snapshot may
    contain minimal data or be empty if rankings are fully computed.

    Returns:
        JSON object with all ranking domain data:
        - modality_rankings: List of all modality rankings
        - course_rankings: List of all course rankings
        - general_rankings: List of all general rankings
    """
    logger.info("snapshot_requested", service="ranking")

    try:
        # Fetch all domain data
        modality_rankings = db.query(ModalityRanking).all()
        course_rankings = db.query(CourseRanking).all()
        general_rankings = db.query(GeneralRanking).all()

        # Convert to dictionaries
        snapshot = {
            "modality_rankings": [
                {
                    "id": str(mr.id),
                    "modality_id": str(mr.modality_id),
                    "season_id": str(mr.season_id),
                    "course_id": str(mr.course_id),
                    "points": mr.points,
                    "details": mr.details,
                    "last_updated": (
                        mr.last_updated.isoformat() if mr.last_updated else None
                    ),
                }
                for mr in modality_rankings
            ],
            "course_rankings": [
                {
                    "id": str(cr.id),
                    "course_id": str(cr.course_id),
                    "season_id": str(cr.season_id),
                    "total_points": cr.total_points,
                    "modality_breakdown": cr.modality_breakdown,
                    "last_updated": (
                        cr.last_updated.isoformat() if cr.last_updated else None
                    ),
                }
                for cr in course_rankings
            ],
            "general_rankings": [
                {
                    "id": str(gr.id),
                    "season_id": str(gr.season_id),
                    "course_id": str(gr.course_id),
                    "position": gr.position,
                    "total_points": gr.total_points,
                    "last_updated": (
                        gr.last_updated.isoformat() if gr.last_updated else None
                    ),
                }
                for gr in general_rankings
            ],
        }

        logger.info(
            "snapshot_generated",
            service="ranking",
            modality_rankings_count=len(modality_rankings),
            course_rankings_count=len(course_rankings),
            general_rankings_count=len(general_rankings),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="ranking", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "ranking"}
