"""
Internal API endpoints for Tournaments Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

import json
from typing import AsyncGenerator

from app.configs.database import get_db_session
from app.configs.logger import logger
from app.models import Tournament, TournamentCompetitor, TournamentRankingPosition
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from taca_snapshots.tournaments import (
    TournamentCompetitorSnapshotItem,
    TournamentRankingPositionSnapshotItem,
    TournamentsSnapshotResponse,
)

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
        tournament_dtos = [t.to_snapshot() for t in tournaments]

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
    Stream complete snapshot of all tournaments data as Server-Sent Events.

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
            "snapshot_stream_requested", service="tournaments", batch_size=batch_size
        )

        try:
            # Count totals for metadata event
            tournament_count = db.query(Tournament).count()
            competitor_count = db.query(TournamentCompetitor).count()
            ranking_position_count = db.query(TournamentRankingPosition).count()

            total_count = tournament_count + competitor_count + ranking_position_count

            # Emit metadata
            yield f"data: {json.dumps({'type': 'metadata', 'count': total_count})}\n\n"

            records_emitted = 0

            # Stream tournaments in batches
            batch = []
            for tournament in db.query(Tournament).yield_per(batch_size):
                batch.append(tournament.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'tournaments'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'tournaments'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream competitors in batches
            batch = []
            for competitor in db.query(TournamentCompetitor).yield_per(batch_size):
                batch.append(competitor.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'competitors'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'competitors'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream ranking positions in batches
            batch = []
            for ranking_position in db.query(TournamentRankingPosition).yield_per(
                batch_size
            ):
                batch.append(ranking_position.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'ranking_positions'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'ranking_positions'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            yield f"data: {json.dumps({'type': 'complete', 'records': records_emitted})}\n\n"
            logger.info(
                "snapshot_stream_completed",
                service="tournaments",
                records_emitted=records_emitted,
            )
        except Exception as e:
            logger.error("snapshot_stream_failed", service="tournaments", error=str(e))
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
    return {"status": "healthy", "service": "tournaments"}
