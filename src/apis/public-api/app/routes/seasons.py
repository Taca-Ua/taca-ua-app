"""
Season routes
"""

from typing import List

from fastapi import APIRouter

from ..schemas import SeasonPublic

router = APIRouter(prefix="/api/public", tags=["Seasons"])


@router.get(
    "/seasons",
    response_model=List[SeasonPublic],
    summary="List seasons",
    description="Get a list of all available seasons/épocas",
)
async def list_seasons():
    """List all available seasons"""
    return [
        {
            "id": 3,
            "year": 2025,
            "display_name": "25/26",
            "is_active": True,
        },
        {
            "id": 2,
            "year": 2024,
            "display_name": "24/25",
            "is_active": False,
        },
        {
            "id": 1,
            "year": 2023,
            "display_name": "23/24",
            "is_active": False,
        },
    ]
