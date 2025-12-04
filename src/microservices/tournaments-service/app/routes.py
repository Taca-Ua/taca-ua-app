"""
API routes for Tournaments Service.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query

router = APIRouter()


@router.post("/tournaments", status_code=201)
async def create_tournament(
    tournament_data: dict,
):
    """
    Create a new tournament.
    """
    return None  # Placeholder for actual implementation


@router.put("/tournaments/{tournament_id}")
async def update_tournament(
    tournament_id: UUID,
    tournament_data: dict,
):
    """
    Update a tournament.
    """
    return None  # Placeholder for actual implementation


@router.post("/tournaments/{tournament_id}/teams")
async def add_teams_to_tournament(
    tournament_id: UUID,
    teams_data: dict,
):
    """
    Add teams to a tournament.
    """
    return None  # Placeholder for actual implementation


@router.delete("/tournaments/{tournament_id}/teams", status_code=204)
async def remove_teams_from_tournament(
    tournament_id: UUID,
    teams_data: dict,
):
    """
    Remove teams from a tournament.
    """
    return None  # Placeholder for actual implementation


@router.post("/tournaments/{tournament_id}/finish")
async def finish_tournament(
    tournament_id: UUID,
    finish_data: dict,
):
    """
    Finish a tournament.
    """
    return None  # Placeholder for actual implementation


@router.get("/tournaments/{tournament_id}")
def get_tournament(
    tournament_id: UUID,
):
    """
    Get a tournament by ID.
    """
    return None  # Placeholder for actual implementation


@router.get("/tournaments")
def list_tournaments(
    modality_id: Optional[UUID] = Query(None),
    season_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List tournaments with optional filters.
    """
    return None  # Placeholder for actual implementation


@router.delete("/tournaments/{tournament_id}", status_code=204)
async def delete_tournament(
    tournament_id: UUID,
):
    """
    Delete a tournament.
    """
    return None  # Placeholder for actual implementations
