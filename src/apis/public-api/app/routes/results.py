"""
Results routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import ResultPublic

router = APIRouter(prefix="/api/public", tags=["Results"])


@router.get(
    "/results",
    response_model=List[ResultPublic],
    summary="Get match results",
    description="Get final results of matches with optional filters",
)
async def list_results(
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
    tournament_id: Optional[int] = Query(None, description="Filter by tournament ID"),
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
):
    """List match results with filters"""
    return [
        {
            "match_id": 2,
            "tournament_id": 1,
            "tournament_name": "Campeonato Futebol 2025",
            "modality_id": 1,
            "modality_name": "Futebol",
            "team_home_id": 1,
            "team_away_id": 3,
            "team_home_name": "MECT A",
            "team_away_name": "MIEET A",
            "course_home_id": 1,
            "course_away_id": 3,
            "home_score": 3,
            "away_score": 1,
            "match_date": datetime(2025, 2, 5, 16, 0),
        },
        {
            "match_id": 4,
            "tournament_id": 1,
            "tournament_name": "Campeonato Futebol 2025",
            "modality_id": 1,
            "modality_name": "Futebol",
            "team_home_id": 2,
            "team_away_id": 3,
            "team_home_name": "LEI A",
            "team_away_name": "MIEET A",
            "course_home_id": 2,
            "course_away_id": 3,
            "home_score": 2,
            "away_score": 2,
            "match_date": datetime(2025, 2, 8, 17, 0),
        },
    ]
