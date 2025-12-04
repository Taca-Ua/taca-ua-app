"""
API routes for Matches Service.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query

router = APIRouter()


@router.post("/matches", status_code=201)
def create_match(match_data: dict):
    """Create a new match."""
    return None  # Placeholder for actual implementation


@router.put("/matches/{match_id}")
def update_match(
    match_id: UUID,
    match_data: dict,
):
    """Update a match."""
    return None  # Placeholder for actual implementation


@router.post("/matches/{match_id}/result")
def register_result(
    match_id: UUID,
    result_data: dict,
):
    """Register result for a match."""
    return None  # Placeholder for actual implementation


@router.post("/matches/{match_id}/lineup")
def assign_lineup(
    match_id: UUID,
    lineup_data: dict,
):
    """Assign lineup for a team in a match."""
    return None  # Placeholder for actual implementation


@router.post(
    "/matches/{match_id}/comments",
    status_code=201,
)
def add_comment(
    match_id: UUID,
    comment_data: dict,
):
    """Add a comment to a match."""
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
):
    """Delete a match."""
    return None  # Placeholder for actual implementation
