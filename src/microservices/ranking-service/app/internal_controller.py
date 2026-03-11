"""
Internal API endpoints for Ranking Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from taca_snapshots.ranking import (
    CourseRankingSnapshotItem,
    GeneralRankingSnapshotItem,
    ModalityRankingSnapshotItem,
    RankingSnapshotResponse,
)

from .database import get_db_session
from .logger import logger
from .models import CourseRanking, GeneralRanking, ModalityRanking

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot", response_model=RankingSnapshotResponse)
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
    Return complete snapshot of all ranking data as strongly typed DTOs.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns all modality rankings, course rankings, and general rankings.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Note: Ranking data might be computed/derived, so this snapshot may
    contain minimal data or be empty if rankings are fully computed.

    Query Parameters:
        limit: Maximum number of records returned per collection (default 10000).
        offset: Number of records to skip (default 0).

    Returns:
        RankingSnapshotResponse with all ranking domain data.
    """
    logger.info("snapshot_requested", service="ranking", limit=limit, offset=offset)

    try:
        # Fetch domain data
        modality_rankings = db.query(ModalityRanking).offset(offset).limit(limit).all()
        course_rankings = db.query(CourseRanking).offset(offset).limit(limit).all()
        general_rankings = db.query(GeneralRanking).offset(offset).limit(limit).all()

        # Build typed DTOs
        modality_ranking_dtos = [
            ModalityRankingSnapshotItem(
                id=str(mr.id),
                modality_id=str(mr.modality_id),
                season_id=str(mr.season_id),
                course_id=str(mr.course_id),
                points=mr.points,
                details=mr.details,
                last_updated=mr.last_updated,
            )
            for mr in modality_rankings
        ]

        course_ranking_dtos = [
            CourseRankingSnapshotItem(
                id=str(cr.id),
                course_id=str(cr.course_id),
                season_id=str(cr.season_id),
                total_points=cr.total_points,
                modality_breakdown=cr.modality_breakdown,
                last_updated=cr.last_updated,
            )
            for cr in course_rankings
        ]

        general_ranking_dtos = [
            GeneralRankingSnapshotItem(
                id=str(gr.id),
                season_id=str(gr.season_id),
                course_id=str(gr.course_id),
                position=gr.position,
                total_points=gr.total_points,
                last_updated=gr.last_updated,
            )
            for gr in general_rankings
        ]

        snapshot = RankingSnapshotResponse(
            modality_rankings=modality_ranking_dtos,
            course_rankings=course_ranking_dtos,
            general_rankings=general_ranking_dtos,
        )

        logger.info(
            "snapshot_generated",
            service="ranking",
            modality_rankings_count=len(modality_ranking_dtos),
            course_rankings_count=len(course_ranking_dtos),
            general_rankings_count=len(general_ranking_dtos),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="ranking", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "ranking"}
