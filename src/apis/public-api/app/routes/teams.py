"""
Team routes
"""

from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import TeamPublic

router = APIRouter(prefix="/api/public", tags=["Teams"])


@router.get(
    "/teams",
    response_model=List[TeamPublic],
    summary="List teams",
    description="Get a list of all teams with optional filters",
)
async def list_teams(
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
):
    """List all teams with optional filters"""
    all_teams = [
        {
            "id": 1,
            "name": "MECT A",
            "course_id": 1,
            "course_name": "Engenharia de Computadores e Telemática",
            "course_short_code": "MECT",
            "modality_id": 1,
            "modality_name": "Futebol",
            "player_count": 11,
        },
        {
            "id": 2,
            "name": "LEI A",
            "course_id": 2,
            "course_name": "Engenharia Informática",
            "course_short_code": "LEI",
            "modality_id": 1,
            "modality_name": "Futebol",
            "player_count": 11,
        },
        {
            "id": 3,
            "name": "MIEET A",
            "course_id": 3,
            "course_name": "Engenharia Eletrónica e Telecomunicações",
            "course_short_code": "MIEET",
            "modality_id": 1,
            "modality_name": "Futebol",
            "player_count": 11,
        },
        {
            "id": 4,
            "name": "MECT B",
            "course_id": 1,
            "course_name": "Engenharia de Computadores e Telemática",
            "course_short_code": "MECT",
            "modality_id": 1,
            "modality_name": "Futebol",
            "player_count": 11,
        },
        {
            "id": 5,
            "name": "MECT A",
            "course_id": 1,
            "course_name": "Engenharia de Computadores e Telemática",
            "course_short_code": "MECT",
            "modality_id": 2,
            "modality_name": "Futsal",
            "player_count": 5,
        },
        {
            "id": 6,
            "name": "LEI A",
            "course_id": 2,
            "course_name": "Engenharia Informática",
            "course_short_code": "LEI",
            "modality_id": 2,
            "modality_name": "Futsal",
            "player_count": 5,
        },
    ]

    # Apply filters
    filtered_teams = all_teams
    if course_id is not None:
        filtered_teams = [t for t in filtered_teams if t["course_id"] == course_id]
    if modality_id is not None:
        filtered_teams = [t for t in filtered_teams if t["modality_id"] == modality_id]

    return filtered_teams
