"""
API routes for Ranking Service.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from . import schemas
from .database import get_db_session
from .events import publish_rankings_updated
from .models import CourseRanking, GeneralRanking, ModalityRanking

router = APIRouter()


@router.post("/rankings/modality/{modality_id}/recalculate")
def recalculate_modality_ranking(
    modality_id: UUID,
    request_data: schemas.RecalculateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Recalculate ranking for a modality."""
    # TODO: Implement actual ranking calculation logic
    # - Fetch all finished matches for this modality
    # - Apply scoring schema
    # - Update modality_ranking table

    background_tasks.add_task(
        publish_rankings_updated,
        season_id=None,
        scope="modality",
        entity_id=modality_id,
    )
    return None


@router.post("/rankings/course/{course_id}/recalculate")
def recalculate_course_ranking(
    course_id: UUID,
    request_data: schemas.RecalculateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Recalculate ranking for a course."""
    # TODO: Implement actual ranking calculation logic
    # - Aggregate points from all modalities for this course
    # - Update course_ranking table

    background_tasks.add_task(
        publish_rankings_updated, season_id=None, scope="course", entity_id=course_id
    )
    return None


@router.post("/rankings/general/recalculate")
def recalculate_general_ranking(
    request_data: schemas.RecalculateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Recalculate general ranking across all courses."""
    # TODO: Implement actual ranking calculation logic
    # - Aggregate all course rankings
    # - Update general_ranking table with positions

    background_tasks.add_task(
        publish_rankings_updated, season_id=None, scope="general", entity_id=None
    )
    return None


@router.get("/rankings/modality/{modality_id}")
def get_modality_ranking(
    modality_id: UUID,
    season_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db_session),
):
    """Get ranking for a modality."""
    query = db.query(ModalityRanking).filter(ModalityRanking.modality_id == modality_id)

    if season_id:
        query = query.filter(ModalityRanking.season_id == season_id)

    rankings = query.order_by(ModalityRanking.points.desc()).all()

    return {
        "rankings": [
            {
                "course_id": str(r.course_id),
                "points": r.points,
                "details": r.details,
                "last_updated": r.last_updated.isoformat(),
            }
            for r in rankings
        ],
        "total": len(rankings),
    }


@router.get("/rankings/course/{course_id}")
def get_course_ranking(
    course_id: UUID,
    season_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db_session),
):
    """Get ranking for a course."""
    query = db.query(CourseRanking).filter(CourseRanking.course_id == course_id)

    if season_id:
        query = query.filter(CourseRanking.season_id == season_id)

    ranking = query.first()

    if not ranking:
        return {
            "course_id": str(course_id),
            "total_points": 0.0,
            "modality_breakdown": {},
        }

    return {
        "course_id": str(ranking.course_id),
        "season_id": str(ranking.season_id),
        "total_points": ranking.total_points,
        "modality_breakdown": ranking.modality_breakdown,
        "last_updated": ranking.last_updated.isoformat(),
    }


@router.get("/rankings/general")
def get_general_ranking(
    season_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db_session),
):
    """Get general ranking across all courses."""
    query = db.query(GeneralRanking)

    if season_id:
        query = query.filter(GeneralRanking.season_id == season_id)

    rankings = query.order_by(GeneralRanking.position.asc()).all()

    return {
        "rankings": [
            {
                "position": r.position,
                "course_id": str(r.course_id),
                "total_points": r.total_points,
                "last_updated": r.last_updated.isoformat(),
            }
            for r in rankings
        ],
        "total": len(rankings),
    }


@router.get("/rankings/history")
def get_ranking_history(
    season_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
):
    """Get historical rankings."""
    query = db.query(GeneralRanking)

    if season_id:
        query = query.filter(GeneralRanking.season_id == season_id)
    if course_id:
        query = query.filter(GeneralRanking.course_id == course_id)

    total = query.count()
    rankings = (
        query.order_by(GeneralRanking.last_updated.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "rankings": [
            {
                "season_id": str(r.season_id),
                "position": r.position,
                "course_id": str(r.course_id),
                "total_points": r.total_points,
                "last_updated": r.last_updated.isoformat(),
            }
            for r in rankings
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
