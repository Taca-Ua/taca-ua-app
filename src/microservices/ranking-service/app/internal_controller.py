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
    Return complete snapshot of all computed ranking data as strongly typed DTOs.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns general rankings, modality rankings, and course rankings derived
    by the ranking-service computation.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.
    """
    logger.info("snapshot_requested", service="ranking", limit=limit, offset=offset)

    general_rows = db.query(GeneralRanking).offset(offset).limit(limit).all()
    modality_rows = db.query(ModalityRanking).offset(offset).limit(limit).all()
    course_rows = db.query(CourseRanking).offset(offset).limit(limit).all()

    snapshot = RankingSnapshotResponse(
        general_rankings=[
            GeneralRankingSnapshotItem(
                course_id=str(r.course_id),
                points=r.points,
            )
            for r in general_rows
        ],
        modality_rankings=[
            ModalityRankingSnapshotItem(
                modality_id=str(r.modality_id),
                course_id=str(r.course_id),
                points=r.points,
            )
            for r in modality_rows
        ],
        course_rankings=[
            CourseRankingSnapshotItem(
                course_id=str(r.course_id),
                points=r.points,
                modality_breakdown=r.modality_breakdown or [],
            )
            for r in course_rows
        ],
    )

    logger.info(
        "snapshot_returned",
        service="ranking",
        general_count=len(snapshot.general_rankings),
        modality_count=len(snapshot.modality_rankings),
        course_count=len(snapshot.course_rankings),
    )

    return snapshot


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "ranking"}
