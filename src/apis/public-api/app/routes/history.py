"""
Historical data routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import HistoricalMatch

router = APIRouter(prefix="/api/public", tags=["Historical Data"])


@router.get(
    "/matches/history",
    response_model=List[HistoricalMatch],
    summary="Get historical matches",
    description="Get matches from previous seasons",
)
async def list_historical_matches(
    season_id: Optional[int] = Query(None, description="Filter by season ID"),
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
):
    """List historical matches"""
    return [
        {
            "id": 100,
            "season_id": 1,
            "season_year": 2024,
            "tournament_name": "Campeonato Futebol 2024",
            "modality_name": "Futebol",
            "team_home_name": "LEI A",
            "team_away_name": "MECT A",
            "course_home_name": "LEI",
            "course_away_name": "MECT",
            "location": "Campo Principal",
            "start_time": datetime(2024, 5, 10, 15, 0),
            "home_score": 2,
            "away_score": 3,
        },
        {
            "id": 101,
            "season_id": 1,
            "season_year": 2024,
            "tournament_name": "Campeonato Futebol 2024",
            "modality_name": "Futebol",
            "team_home_name": "MECT A",
            "team_away_name": "MIEET A",
            "course_home_name": "MECT",
            "course_away_name": "MIEET",
            "location": "Campo 2",
            "start_time": datetime(2024, 5, 15, 16, 0),
            "home_score": 4,
            "away_score": 1,
        },
    ]
