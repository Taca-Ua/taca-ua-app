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
    """List tournaments with filters

    Returns tournaments filtered by modality_id and/or season_id.
    For now this returns static example data - the filtering logic demonstrates
    how the API should behave when real DB queries are implemented.
    """
    # Mock tournament database
    all_tournaments = [
        # Season 3 (25/26) - Modality 1 (Futebol)
        {
            "id": 1,
            "name": "Campeonato Futebol 25/26",
            "modality": {"id": 1, "name": "Futebol"},
            "season": {"id": 3, "year": 2025, "display_name": "25/26"},
            "status": "active",
            "start_date": datetime(2025, 2, 1, 10, 0),
            "team_count": 8,
        },
        # Season 3 (25/26) - Modality 2 (Futsal)
        {
            "id": 2,
            "name": "Campeonato Futsal 25/26",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 3, "year": 2025, "display_name": "25/26"},
            "status": "active",
            "start_date": datetime(2025, 3, 1, 10, 0),
            "team_count": 10,
        },
        {
            "id": 3,
            "name": "Taça Futsal 25/26",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 3, "year": 2025, "display_name": "25/26"},
            "status": "active",
            "start_date": datetime(2025, 4, 1, 10, 0),
            "team_count": 6,
        },
        # Season 2 (24/25) - Modality 1 (Futebol)
        {
            "id": 4,
            "name": "Campeonato Futebol 24/25",
            "modality": {"id": 1, "name": "Futebol"},
            "season": {"id": 2, "year": 2024, "display_name": "24/25"},
            "status": "completed",
            "start_date": datetime(2024, 2, 1, 10, 0),
            "team_count": 8,
        },
        # Season 2 (24/25) - Modality 2 (Futsal)
        {
            "id": 5,
            "name": "Campeonato Futsal 24/25",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 2, "year": 2024, "display_name": "24/25"},
            "status": "completed",
            "start_date": datetime(2024, 3, 1, 10, 0),
            "team_count": 10,
        },
    ]

    # Apply filters
    filtered = all_tournaments
    if modality_id is not None:
        filtered = [t for t in filtered if t["modality"]["id"] == modality_id]
    if season_id is not None:
        filtered = [t for t in filtered if t["season"]["id"] == season_id]

    return filtered


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
        "tournament_id": tournament_id,
        "tournament_name": "Campeonato Futebol 2025",
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
