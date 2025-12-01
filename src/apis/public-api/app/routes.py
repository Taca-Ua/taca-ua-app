"""
Routes for Public Data API
All endpoints follow the API_ENDPOINTS.md specification
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from .schemas import (
    CoursePublic,
    CourseRanking,
    GeneralRanking,
    HistoricalMatch,
    HistoricalRanking,
    MatchPublicDetail,
    MatchPublicList,
    ModalityPublic,
    ModalityRanking,
    RegulationPublic,
    ResultPublic,
    TournamentPublicDetail,
    TournamentPublicList,
)

router = APIRouter(prefix="/api/public", tags=["Public API"])


# ================== 1. Calendar (RF5.1) ==================


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


# ================== 2. Results (RF5.2) ==================


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


# ================== 3. Rankings (RF5.3–5.5) ==================


@router.get(
    "/rankings/modality/{modality_id}",
    response_model=ModalityRanking,
    summary="Get ranking by modality",
    description="Get current rankings for a specific modality",
)
async def get_modality_ranking(modality_id: int):
    """Get ranking for a specific modality"""
    return {
        "modality_id": modality_id,
        "modality_name": "Futebol",
        "rankings": [
            {
                "position": 1,
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
    }


@router.get(
    "/rankings/course/{course_id}",
    response_model=CourseRanking,
    summary="Get ranking by course",
    description="Get current rankings for a specific course across all modalities",
)
async def get_course_ranking(course_id: int):
    """Get ranking for a specific course"""
    return {
        "course_id": course_id,
        "course_name": "MECT",
        "modalities": [
            {
                "modality_id": 1,
                "modality_name": "Futebol",
                "rankings": [
                    {
                        "position": 1,
                        "course_id": course_id,
                        "course_name": "MECT",
                        "course_short_code": "MECT",
                        "points": 15,
                        "played": 5,
                        "won": 5,
                        "drawn": 0,
                        "lost": 0,
                    }
                ],
            },
            {
                "modality_id": 2,
                "modality_name": "Futsal",
                "rankings": [
                    {
                        "position": 2,
                        "course_id": course_id,
                        "course_name": "MECT",
                        "course_short_code": "MECT",
                        "points": 12,
                        "played": 5,
                        "won": 4,
                        "drawn": 0,
                        "lost": 1,
                    }
                ],
            },
        ],
        "total_points": 27,
    }


@router.get(
    "/rankings/general",
    response_model=GeneralRanking,
    summary="Get general ranking",
    description="Get current general ranking across all courses",
)
async def get_general_ranking():
    """Get general ranking"""
    return {
        "season_id": 2,
        "season_year": 2025,
        "rankings": [
            {
                "position": 1,
                "course_id": 1,
                "course_name": "MECT",
                "course_short_code": "MECT",
                "points": 87,
                "played": 30,
                "won": 27,
                "drawn": 6,
                "lost": 3,
            },
            {
                "position": 2,
                "course_id": 2,
                "course_name": "LEI",
                "course_short_code": "LEI",
                "points": 75,
                "played": 30,
                "won": 23,
                "drawn": 6,
                "lost": 7,
            },
            {
                "position": 3,
                "course_id": 3,
                "course_name": "MIEET",
                "course_short_code": "MIEET",
                "points": 62,
                "played": 30,
                "won": 19,
                "drawn": 5,
                "lost": 11,
            },
        ],
    }


@router.get(
    "/rankings/general/history",
    response_model=List[HistoricalRanking],
    summary="Get historical rankings",
    description="Get rankings from previous seasons",
)
async def get_historical_rankings(
    season_id: Optional[int] = Query(None, description="Filter by season ID"),
):
    """Get historical rankings"""
    return [
        {
            "season_id": 1,
            "season_year": 2024,
            "winner_course_id": 2,
            "winner_course_name": "LEI",
            "rankings": [
                {
                    "position": 1,
                    "course_id": 2,
                    "course_name": "LEI",
                    "course_short_code": "LEI",
                    "points": 92,
                    "played": 30,
                    "won": 28,
                    "drawn": 8,
                    "lost": 2,
                },
                {
                    "position": 2,
                    "course_id": 1,
                    "course_name": "MECT",
                    "course_short_code": "MECT",
                    "points": 85,
                    "played": 30,
                    "won": 26,
                    "drawn": 7,
                    "lost": 4,
                },
            ],
        }
    ]


# ================== 4. Tournaments ==================


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
        "rules": "Formato eliminat\u00f3ria dupla",
        "start_date": datetime(2025, 2, 1, 10, 0),
        "teams": [1, 2, 3, 4],
        "team_names": ["MECT A", "LEI A", "MIEET A", "MECT B"],
    }


# ================== 5. Modalities ==================


@router.get(
    "/modalities",
    response_model=List[ModalityPublic],
    summary="List modalities",
    description="Get a list of all available modalities",
)
async def list_modalities():
    """List all modalities"""
    return [
        {
            "id": 1,
            "name": "Futebol",
            "type": "coletiva",
            "description": "Futebol de 11",
        },
        {"id": 2, "name": "Futsal", "type": "coletiva", "description": "Futsal de 5"},
        {
            "id": 3,
            "name": "T\u00e9nis",
            "type": "individual",
            "description": "T\u00e9nis individual",
        },
    ]


# ================== 6. Courses ==================


@router.get(
    "/courses",
    response_model=List[CoursePublic],
    summary="List courses",
    description="Get a list of all courses",
)
async def list_courses():
    """List all courses"""
    return [
        {
            "id": 1,
            "name": "Engenharia de Computadores e Telem\u00e1tica",
            "short_code": "MECT",
            "color": "#FF5733",
        },
        {
            "id": 2,
            "name": "Engenharia Inform\u00e1tica",
            "short_code": "LEI",
            "color": "#33FF57",
        },
        {
            "id": 3,
            "name": "Engenharia Eletr\u00f3nica e Telecomunica\u00e7\u00f5es",
            "short_code": "MIEET",
            "color": "#3357FF",
        },
    ]


# ================== 7. Regulations (RF5.6) ==================


@router.get(
    "/regulations",
    response_model=List[RegulationPublic],
    summary="List regulations",
    description="Get a list of regulations with optional modality filter",
)
async def list_regulations(
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
):
    """List regulations with optional modality filter"""
    return [
        {
            "id": 1,
            "title": "Regulamento Futebol",
            "description": "Regras do futebol TACA",
            "modality_id": 1,
            "modality_name": "Futebol",
            "file_url": "http://example.com/reg1.pdf",
            "created_at": datetime(2025, 1, 15, 10, 0),
        },
        {
            "id": 2,
            "title": "Regulamento Futsal",
            "description": "Regras do futsal TACA",
            "modality_id": 2,
            "modality_name": "Futsal",
            "file_url": "http://example.com/reg2.pdf",
            "created_at": datetime(2025, 1, 20, 10, 0),
        },
    ]


@router.get(
    "/regulations/{regulation_id}",
    summary="Get regulation file",
    description="Download regulation PDF file",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Regulation PDF file",
        }
    },
)
async def get_regulation_file(regulation_id: int):
    """Get regulation file (PDF)"""
    return {"message": "PDF download not implemented"}


# ================== 8. Historical Data ==================


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
