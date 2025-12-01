"""
Routes for Public Data API
All endpoints follow the API_ENDPOINTS.md specification
"""

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
    return []


@router.get(
    "/matches/today",
    response_model=List[MatchPublicList],
    summary="Get today's matches",
    description="Get all matches scheduled for today",
)
async def list_today_matches():
    """Get today's matches"""
    return []


@router.get(
    "/matches/{match_id}",
    response_model=MatchPublicDetail,
    summary="Get match details",
    description="Get detailed information about a specific match",
)
async def get_match_detail(match_id: int):
    """Get match details by ID"""
    return {}


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
    return []


# ================== 3. Rankings (RF5.3–5.5) ==================


@router.get(
    "/rankings/modality/{modality_id}",
    response_model=ModalityRanking,
    summary="Get ranking by modality",
    description="Get current rankings for a specific modality",
)
async def get_modality_ranking(modality_id: int):
    """Get ranking for a specific modality"""
    return {}


@router.get(
    "/rankings/course/{course_id}",
    response_model=CourseRanking,
    summary="Get ranking by course",
    description="Get current rankings for a specific course across all modalities",
)
async def get_course_ranking(course_id: int):
    """Get ranking for a specific course"""
    return {}


@router.get(
    "/rankings/general",
    response_model=GeneralRanking,
    summary="Get general ranking",
    description="Get current general ranking across all courses",
)
async def get_general_ranking():
    """Get general ranking"""
    return {}


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
    return []


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
    return []


@router.get(
    "/tournaments/{tournament_id}",
    response_model=TournamentPublicDetail,
    summary="Get tournament details",
    description="Get detailed information about a specific tournament",
)
async def get_tournament_detail(tournament_id: int):
    """Get tournament details by ID"""
    return {}


# ================== 5. Modalities ==================


@router.get(
    "/modalities",
    response_model=List[ModalityPublic],
    summary="List modalities",
    description="Get a list of all available modalities",
)
async def list_modalities():
    """List all modalities"""
    return []


# ================== 6. Courses ==================


@router.get(
    "/courses",
    response_model=List[CoursePublic],
    summary="List courses",
    description="Get a list of all courses",
)
async def list_courses():
    """List all courses"""
    return []


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
    return []


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
    return []
