"""
Tournament routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import TournamentPublicDetail, TournamentPublicList

router = APIRouter(prefix="/api/public", tags=["Tournaments"])


@router.get(
    "/tournaments",
    response_model=List[TournamentPublicList],
    summary="List tournaments",
    description="Get a list of tournaments with optional filters",
)
async def list_tournaments(
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
    season_id: Optional[int] = Query(None, description="Filter by season ID"),
):
    """List tournaments with filters"""
    return [
        {
            "id": 1,
            "name": "Campeonato Futebol 2025",
            "modality_id": 1,
            "modality_name": "Futebol",
            "season_id": 2,
            "season_year": 2025,
            "status": "active",
            "start_date": datetime(2025, 2, 1, 10, 0),
        },
        {
            "id": 2,
            "name": "Campeonato Futsal 2025",
            "modality_id": 2,
            "modality_name": "Futsal",
            "season_id": 2,
            "season_year": 2025,
            "status": "active",
            "start_date": datetime(2025, 3, 1, 10, 0),
        },
    ]


@router.get(
    "/tournaments/{tournament_id}",
    response_model=TournamentPublicDetail,
    summary="Get tournament details",
    description="Get detailed information about a specific tournament",
)
async def get_tournament_detail(tournament_id: int):
    """Get tournament details by ID"""
    return {
        "id": tournament_id,
        "name": "Campeonato Futebol 2025",
        "modality_id": 1,
        "modality_name": "Futebol",
        "season_id": 2,
        "season_year": 2025,
        "status": "active",
        "rules": "Formato eliminatória dupla",
        "start_date": datetime(2025, 2, 1, 10, 0),
        "teams": [1, 2, 3, 4],
        "team_names": ["MECT A", "LEI A", "MIEET A", "MECT B"],
    }
