"""
Tournament routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import TournamentPublicDetail, TournamentPublicList, TournamentRankings

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
    description="Get detailed information about a specific tournament including rankings",
)
async def get_tournament_detail(
    tournament_id: int,
    include_rankings: bool = Query(
        True, description="Include tournament rankings in response"
    ),
):
    """Get tournament details by ID with optional rankings"""
    rankings = None
    if include_rankings:
        rankings = [
            {
                "position": 1,
                "team_id": 1,
                "team_name": "MECT A",
                "course_id": 1,
                "course_name": "MECT",
                "course_short_code": "MECT",
                "points": 15,
                "played": 5,
                "won": 5,
                "drawn": 0,
                "lost": 0,
            },
            {
                "position": 2,
                "team_id": 2,
                "team_name": "LEI A",
                "course_id": 2,
                "course_name": "LEI",
                "course_short_code": "LEI",
                "points": 10,
                "played": 5,
                "won": 3,
                "drawn": 1,
                "lost": 1,
            },
            {
                "position": 3,
                "team_id": 3,
                "team_name": "MIEET A",
                "course_id": 3,
                "course_name": "MIEET",
                "course_short_code": "MIEET",
                "points": 7,
                "played": 5,
                "won": 2,
                "drawn": 1,
                "lost": 2,
            },
        ]

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
        "rankings": rankings,
    }


@router.get(
    "/tournaments/{tournament_id}/rankings",
    response_model=TournamentRankings,
    summary="Get tournament rankings",
    description="Get current rankings/standings for a specific tournament",
)
async def get_tournament_rankings(tournament_id: int):
    """Get rankings for a specific tournament"""
    return {
        "tournament_id": tournament_id,
        "tournament_name": "Campeonato Futebol 2025",
        "modality_id": 1,
        "modality_name": "Futebol",
        "season_id": 2,
        "season_year": 2025,
        "rankings": [
            {
                "position": 1,
                "team_id": 1,
                "team_name": "MECT A",
                "course_id": 1,
                "course_name": "MECT",
                "course_short_code": "MECT",
                "points": 15,
                "played": 5,
                "won": 5,
                "drawn": 0,
                "lost": 0,
            },
            {
                "position": 2,
                "team_id": 2,
                "team_name": "LEI A",
                "course_id": 2,
                "course_name": "LEI",
                "course_short_code": "LEI",
                "points": 10,
                "played": 5,
                "won": 3,
                "drawn": 1,
                "lost": 1,
            },
            {
                "position": 3,
                "team_id": 3,
                "team_name": "MIEET A",
                "course_id": 3,
                "course_name": "MIEET",
                "course_short_code": "MIEET",
                "points": 7,
                "played": 5,
                "won": 2,
                "drawn": 1,
                "lost": 2,
            },
            {
                "position": 4,
                "team_id": 4,
                "team_name": "MECT B",
                "course_id": 1,
                "course_name": "MECT",
                "course_short_code": "MECT",
                "points": 3,
                "played": 5,
                "won": 1,
                "drawn": 0,
                "lost": 4,
            },
        ],
    }
