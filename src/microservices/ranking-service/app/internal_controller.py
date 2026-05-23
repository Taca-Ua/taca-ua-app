"""
Internal API endpoints for Ranking Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
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


@router.get("/snapshot/stream")
def stream_snapshot(
    db: Session = Depends(get_db_session),
    batch_size: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Number of records to emit per event",
    ),
):
    """
    Stream complete snapshot of all ranking data as Server-Sent Events.

    Event Types:
    - metadata: {"type": "metadata", "count": <total_items>}
    - batch: {"type": "batch", "items": [...]}
    - complete: {"type": "complete", "records": <total_count>}

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Query Parameters:
        batch_size: Number of records per batch event (default 100).

    Returns:
        text/event-stream with snapshot data in JSON batches.
    """

    async def event_stream() -> AsyncGenerator[str, None]:
        logger.info(
            "snapshot_stream_requested", service="ranking", batch_size=batch_size
        )

        try:
            # Count totals for metadata event
            general_ranking_count = db.query(GeneralRanking).count()
            modality_ranking_count = db.query(ModalityRanking).count()
            course_ranking_count = db.query(CourseRanking).count()

            total_count = (
                general_ranking_count + modality_ranking_count + course_ranking_count
            )

            # Emit metadata
            yield f"data: {json.dumps({'type': 'metadata', 'count': total_count})}\n\n"

            records_emitted = 0

            # Stream general rankings in batches
            batch = []
            for general_ranking in db.query(GeneralRanking).yield_per(batch_size):
                batch.append(general_ranking.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'general_rankings'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'general_rankings'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream modality rankings in batches
            batch = []
            for modality_ranking in db.query(ModalityRanking).yield_per(batch_size):
                batch.append(modality_ranking.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'modality_rankings'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'modality_rankings'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream course rankings in batches
            batch = []
            for course_ranking in db.query(CourseRanking).yield_per(batch_size):
                batch.append(course_ranking.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'course_rankings'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'course_rankings'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            yield f"data: {json.dumps({'type': 'complete', 'records': records_emitted})}\n\n"
            logger.info(
                "snapshot_stream_completed",
                service="ranking",
                records_emitted=records_emitted,
            )
        except Exception as e:
            logger.error("snapshot_stream_failed", service="ranking", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "ranking"}
