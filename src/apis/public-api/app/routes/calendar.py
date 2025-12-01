"""
Calendar/Matches routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import MatchPublicDetail, MatchPublicList

router = APIRouter(prefix="/api/public", tags=["Calendar"])


@router.get(
    "/matches",
    response_model=List[MatchPublicList],
    summary="List matches with filters",
    description="Get a list of matches filtered by date, modality, course, team, or status",
)
async def list_matches(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    status: Optional[str] = Query(
        None, description="Filter by status (scheduled, finished)"
    ),
    limit: Optional[int] = Query(50, description="Number of results to return"),
    offset: Optional[int] = Query(0, description="Number of results to skip"),
):
    """List matches with optional filters"""
    dummy_matches = [
        {
            "id": 1,
            "tournament_id": 1,
            "modality_id": 1,
            "team_home_id": 1,
            "team_away_id": 2,
            "team_home_name": "MECT A",
            "team_away_name": "LEI A",
            "course_home_id": 1,
            "course_away_id": 2,
            "location": "Campo 1",
            "start_time": datetime(2025, 2, 10, 15, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 2,
            "tournament_id": 1,
            "modality_id": 1,
            "team_home_id": 1,
            "team_away_id": 3,
            "team_home_name": "MECT A",
            "team_away_name": "MIEET A",
            "course_home_id": 1,
            "course_away_id": 3,
            "location": "Campo 2",
            "start_time": datetime(2025, 2, 5, 16, 0),
            "status": "finished",
            "home_score": 3,
            "away_score": 1,
        },
    ]
    dummy_matches = [
        i for i in dummy_matches if status is None or i["status"] == status
    ]
    return dummy_matches[offset : offset + limit]


@router.get(
    "/matches/today",
    response_model=List[MatchPublicList],
    summary="Get today's matches",
    description="Get all matches scheduled for today",
)
async def list_today_matches():
    """Get today's matches"""
    return [
        {
            "id": 5,
            "tournament_id": 1,
            "modality_id": 1,
            "team_home_id": 2,
            "team_away_id": 3,
            "team_home_name": "LEI A",
            "team_away_name": "MIEET A",
            "course_home_id": 2,
            "course_away_id": 3,
            "location": "Campo Principal",
            "start_time": datetime(2025, 12, 1, 18, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        }
    ]


@router.get(
    "/matches/{match_id}",
    response_model=MatchPublicDetail,
    summary="Get match details",
    description="Get detailed information about a specific match",
)
async def get_match_detail(match_id: int):
    """Get match details by ID"""
    return {
        "id": match_id,
        "tournament_id": 1,
        "tournament_name": "Campeonato Futebol 2025",
        "modality_id": 1,
        "modality_name": "Futebol",
        "team_home_id": 1,
        "team_away_id": 2,
        "team_home_name": "MECT A",
        "team_away_name": "LEI A",
        "course_home_id": 1,
        "course_away_id": 2,
        "course_home_name": "MECT",
        "course_away_name": "LEI",
        "location": "Campo 1",
        "start_time": datetime(2025, 2, 10, 15, 0),
        "status": "finished",
        "home_score": 2,
        "away_score": 1,
        "comments": ["Great match!", "Intense competition"],
    }
