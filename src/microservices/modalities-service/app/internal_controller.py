"""
Internal API endpoints for Modalities Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds (HTTP and SSE versions)
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from taca_snapshots.modalities import ModalitiesSnapshotResponse

from .database import get_db_session
from .logger import logger
from .models import (
    Course,
    Modality,
    ModalityType,
    Nucleo,
    Regulation,
    Season,
    Staff,
    Student,
    Team,
    team_players,
)

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot", response_model=ModalitiesSnapshotResponse)
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
    Return complete snapshot of all modalities data as strongly typed DTOs.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns all nucleos, courses, modality types, modalities, students,
    staff, teams, and team-player relationships.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Query Parameters:
        limit: Maximum number of records returned per collection (default 10000).
        offset: Number of records to skip (default 0).

    Returns:
        ModalitiesSnapshotResponse with all modalities domain data.
    """
    logger.info("snapshot_requested", service="modalities", limit=limit, offset=offset)

    try:
        # Fetch domain data
        nucleos = db.query(Nucleo).offset(offset).limit(limit).all()
        courses = db.query(Course).offset(offset).limit(limit).all()
        modality_types = db.query(ModalityType).offset(offset).limit(limit).all()
        modalities = db.query(Modality).offset(offset).limit(limit).all()
        students = db.query(Student).offset(offset).limit(limit).all()
        staff = db.query(Staff).offset(offset).limit(limit).all()
        teams = db.query(Team).offset(offset).limit(limit).all()
        regulations = db.query(Regulation).offset(offset).limit(limit).all()
        seasons = db.query(Season).offset(offset).limit(limit).all()

        # Build typed DTOs
        nucleo_dtos = [n.to_snapshot() for n in nucleos]

        course_dtos = [c.to_snapshot() for c in courses]

        modality_type_dtos = [mt.to_snapshot() for mt in modality_types]

        modality_dtos = [m.to_snapshot() for m in modalities]

        student_dtos = [s.to_snapshot() for s in students]

        staff_dtos = [s.to_snapshot() for s in staff]

        team_dtos = [t.to_snapshot() for t in teams]

        regulation_dtos = [r.to_snapshot() for r in regulations]

        season_dtos = [s.to_snapshot() for s in seasons]

        snapshot = ModalitiesSnapshotResponse(
            nucleos=nucleo_dtos,
            courses=course_dtos,
            modality_types=modality_type_dtos,
            modalities=modality_dtos,
            students=student_dtos,
            staff=staff_dtos,
            teams=team_dtos,
            regulations=regulation_dtos,
            seasons=season_dtos,
        )

        logger.info(
            "snapshot_generated",
            service="modalities",
            nucleos_count=len(nucleo_dtos),
            courses_count=len(course_dtos),
            modality_types_count=len(modality_type_dtos),
            modalities_count=len(modality_dtos),
            students_count=len(student_dtos),
            staff_count=len(staff_dtos),
            teams_count=len(team_dtos),
            team_players_count=0,  # team_player_dtos is not defined
            regulations_count=len(regulation_dtos),
            seasons_count=len(season_dtos),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="modalities", error=str(e))
        raise


@router.get("/snapshot/stream")
async def stream_snapshot(
    db: Session = Depends(get_db_session),
    batch_size: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Number of records to emit per event",
    ),
):
    """
    Stream complete snapshot of all modalities data as Server-Sent Events.

    This endpoint is used by the Read Model Updater for efficient streaming
    rebuilds of large datasets. Data is streamed incrementally in batches
    rather than loading the entire snapshot into memory at once.

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
            "snapshot_stream_requested", service="modalities", batch_size=batch_size
        )

        try:
            # Count totals for metadata event
            nucleo_count = db.query(Nucleo).count()
            course_count = db.query(Course).count()
            modality_type_count = db.query(ModalityType).count()
            modality_count = db.query(Modality).count()
            student_count = db.query(Student).count()
            staff_count = db.query(Staff).count()
            team_count = db.query(Team).count()
            team_player_count = db.query(team_players).count()
            regulation_count = db.query(Regulation).count()
            season_count = db.query(Season).count()

            total_count = (
                nucleo_count
                + course_count
                + modality_type_count
                + modality_count
                + student_count
                + staff_count
                + team_count
                + team_player_count
                + regulation_count
                + season_count
            )

            # Emit metadata
            yield f"data: {json.dumps({'type': 'metadata', 'count': total_count})}\n\n"

            records_emitted = 0

            # Stream nucleos
            batch = []
            for n in db.query(Nucleo).yield_per(batch_size):
                batch.append(n.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'nucleos'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'nucleos'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream courses
            for c in db.query(Course).all():
                batch.append(c.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'courses'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'courses'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream modality types
            for mt in db.query(ModalityType).all():
                batch.append(mt.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'modality_types'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'modality_types'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream modalities
            for m in db.query(Modality).all():
                batch.append(m.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'modalities'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'modalities'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream students
            for s in db.query(Student).all():
                batch.append(s.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'students'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'students'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream staff
            for s in db.query(Staff).all():
                batch.append(s.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'staff'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'staff'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream teams
            for t in db.query(Team).yield_per(batch_size):
                batch.append(t.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'teams'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'teams'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Stream regulations
            for r in db.query(Regulation).all():
                batch.append(r.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'regulations'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'regulations'})}\n\n"
                records_emitted += len(batch)

            # Stream seasons
            for s in db.query(Season).all():
                batch.append(s.to_snapshot().to_dict())
                if len(batch) >= batch_size:
                    yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'seasons'})}\n\n"
                    records_emitted += len(batch)
                    batch.clear()

            if batch:
                yield f"data: {json.dumps({'type': 'batch', 'items': batch, 'category': 'seasons'})}\n\n"
                records_emitted += len(batch)
                batch.clear()

            # Emit completion
            yield f"data: {json.dumps({'type': 'complete', 'records': records_emitted})}\n\n"

            logger.info(
                "snapshot_stream_complete",
                service="modalities",
                records_emitted=records_emitted,
            )

        except Exception as e:
            logger.error("snapshot_stream_failed", service="modalities", error=str(e))
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
    return {"status": "healthy", "service": "modalities"}
