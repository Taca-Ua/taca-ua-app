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
            "season": {"id": 3, "year": 2025},
            "status": "active",
            "start_date": datetime(2025, 2, 1, 10, 0),
            "team_count": 8,
        },
        # Season 3 (25/26) - Modality 2 (Futsal)
        {
            "id": 2,
            "name": "Campeonato Futsal 25/26",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 3, "year": 2025},
            "status": "active",
            "start_date": datetime(2025, 3, 1, 10, 0),
            "team_count": 10,
        },
        {
            "id": 3,
            "name": "Taça Futsal 25/26",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 3, "year": 2025},
            "status": "active",
            "start_date": datetime(2025, 4, 1, 10, 0),
            "team_count": 6,
        },
        # Season 2 (24/25) - Modality 1 (Futebol)
        {
            "id": 4,
            "name": "Campeonato Futebol 24/25",
            "modality": {"id": 1, "name": "Futebol"},
            "season": {"id": 2, "year": 2024},
            "status": "completed",
            "start_date": datetime(2024, 2, 1, 10, 0),
            "team_count": 8,
        },
        # Season 2 (24/25) - Modality 2 (Futsal)
        {
            "id": 5,
            "name": "Campeonato Futsal 24/25",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 2, "year": 2024},
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
    """Get tournament details by ID with optional rankings

    Looks up tournament from mock database and returns details with optional rankings.
    """
    # Mock tournament database - same as in list_tournaments
    all_tournaments = {
        1: {
            "id": 1,
            "name": "Campeonato Futebol 25/26",
            "modality": {"id": 1, "name": "Futebol"},
            "season": {"id": 3, "year": 2025},
            "status": "active",
            "rules": "Sistema de pontos: Vitória 3pts, Empate 1pt",
            "start_date": datetime(2025, 2, 1, 10, 0),
            "team_count": 8,
        },
        2: {
            "id": 2,
            "name": "Campeonato Futsal 25/26",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 3, "year": 2025},
            "status": "active",
            "rules": "Formato eliminatória dupla com fase de grupos",
            "start_date": datetime(2025, 3, 1, 10, 0),
            "team_count": 10,
        },
        3: {
            "id": 3,
            "name": "Taça Futsal 25/26",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 3, "year": 2025},
            "status": "active",
            "rules": "Eliminatória simples - jogos únicos",
            "start_date": datetime(2025, 4, 1, 10, 0),
            "team_count": 6,
        },
        4: {
            "id": 4,
            "name": "Campeonato Futebol 24/25",
            "modality": {"id": 1, "name": "Futebol"},
            "season": {"id": 2, "year": 2024},
            "status": "completed",
            "rules": "Sistema de pontos: Vitória 3pts, Empate 1pt",
            "start_date": datetime(2024, 2, 1, 10, 0),
            "team_count": 8,
        },
        5: {
            "id": 5,
            "name": "Campeonato Futsal 24/25",
            "modality": {"id": 2, "name": "Futsal"},
            "season": {"id": 2, "year": 2024},
            "status": "completed",
            "rules": "Formato eliminatória dupla com fase de grupos",
            "start_date": datetime(2024, 3, 1, 10, 0),
            "team_count": 10,
        },
    }

    # Mock rankings per tournament
    tournament_rankings = {
        1: [  # Futebol 25/26
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
        ],
        2: [  # Futsal 25/26
            {
                "position": 1,
                "team_id": 4,
                "team_name": "LEI Futsal A",
                "course_id": 2,
                "course_name": "LEI",
                "course_short_code": "LEI",
                "points": 18,
                "played": 6,
                "won": 6,
                "drawn": 0,
                "lost": 0,
            },
            {
                "position": 2,
                "team_id": 5,
                "team_name": "MECT Futsal A",
                "course_id": 1,
                "course_name": "MECT",
                "course_short_code": "MECT",
                "points": 13,
                "played": 6,
                "won": 4,
                "drawn": 1,
                "lost": 1,
            },
            {
                "position": 3,
                "team_id": 6,
                "team_name": "MIEET Futsal A",
                "course_id": 3,
                "course_name": "MIEET",
                "course_short_code": "MIEET",
                "points": 10,
                "played": 6,
                "won": 3,
                "drawn": 1,
                "lost": 2,
            },
        ],
        3: [  # Taça Futsal 25/26
            {
                "position": 1,
                "team_id": 7,
                "team_name": "MIEET Futsal B",
                "course_id": 3,
                "course_name": "MIEET",
                "course_short_code": "MIEET",
                "points": 9,
                "played": 3,
                "won": 3,
                "drawn": 0,
                "lost": 0,
            },
            {
                "position": 2,
                "team_id": 8,
                "team_name": "LEI Futsal B",
                "course_id": 2,
                "course_name": "LEI",
                "course_short_code": "LEI",
                "points": 6,
                "played": 3,
                "won": 2,
                "drawn": 0,
                "lost": 1,
            },
        ],
    }

    # Find tournament
    tournament = all_tournaments.get(tournament_id)
    if not tournament:
        # Return a default if not found (in production this would raise 404)
        return {
            "id": tournament_id,
            "name": f"Torneio {tournament_id}",
            "modality": {"id": 1, "name": "Desconhecido"},
            "season": {"id": 1, "year": 2025, "display_name": "25/26"},
            "status": "unknown",
            "rules": None,
            "start_date": None,
            "team_count": 0,
            "rankings": [],
        }

    # Add rankings if requested
    result = tournament.copy()
    if include_rankings:
        result["rankings"] = tournament_rankings.get(tournament_id, [])
    else:
        result["rankings"] = None

    return result


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
