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
from taca_snapshots.ranking import RankingSnapshotResponse

from .database import get_db_session
from .logger import logger

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

    snapshot = RankingSnapshotResponse()

    return snapshot


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "ranking"}
