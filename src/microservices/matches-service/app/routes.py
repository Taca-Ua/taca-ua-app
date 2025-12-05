"""
API routes for Matches Service.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Query

from .events import (
    publish_match_cancelled,
    publish_match_created,
    publish_match_finished,
    publish_match_updated,
)

router = APIRouter()


@router.post("/matches", status_code=201)
def create_match(match_data: dict, background_tasks: BackgroundTasks):
    """Create a new match."""

    background_tasks.add_task(publish_match_created, None)
    return None  # Placeholder for actual implementation


@router.put("/matches/{match_id}")
def update_match(
    match_id: UUID,
    match_data: dict,
    background_tasks: BackgroundTasks,
):
    """Update a match."""

    background_tasks.add_task(publish_match_updated, None, {})
    return None  # Placeholder for actual implementation


@router.post("/matches/{match_id}/result")
def register_result(
    match_id: UUID,
    result_data: dict,
    background_tasks: BackgroundTasks,
):
    """Register result for a match."""

    background_tasks.add_task(publish_match_finished, None)
    return None  # Placeholder for actual implementation


@router.post("/matches/{match_id}/lineup")
def assign_lineup(
    match_id: UUID,
    lineup_data: dict,
    background_tasks: BackgroundTasks,
):
    """Assign lineup for a team in a match."""

    background_tasks.add_task(publish_match_updated, None, {})
    return None  # Placeholder for actual implementation


@router.post(
    "/matches/{match_id}/comments",
    status_code=201,
)
def add_comment(
    match_id: UUID,
    comment_data: dict,
    background_tasks: BackgroundTasks,
):
    """Add a comment to a match."""

    background_tasks.add_task(publish_match_updated, None, {})
    return None  # Placeholder for actual implementation


@router.get("/matches/{match_id}")
def get_match(
    match_id: UUID,
):
    """Get a match by ID."""
    return None  # Placeholder for actual implementation


@router.get("/matches")
def list_matches(
    tournament_id: Optional[UUID] = Query(None),
    modality_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    date: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List matches with optional filters."""
    return None  # Placeholder for actual implementation


@router.get("/matches/{match_id}/sheet")
def generate_match_sheet(
    match_id: UUID,
    format: str = Query("pdf", regex="^(pdf|json)$"),
):
    """Generate match sheet (PDF or JSON)."""
    return None  # Placeholder for actual implementation


@router.delete("/matches/{match_id}", status_code=204)
def delete_match(
    match_id: UUID,
    background_tasks: BackgroundTasks,
):
    """Delete a match."""

    background_tasks.add_task(publish_match_cancelled, str(match_id), "Deleted by user")
    return None  # Placeholder for actual implementation
