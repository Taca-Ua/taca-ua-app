"""
Rankings routes
"""

from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import CourseRanking, GeneralRanking, HistoricalRanking, ModalityRanking

router = APIRouter(prefix="/api/public", tags=["Rankings"])


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
