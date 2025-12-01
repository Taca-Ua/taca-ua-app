"""
Course routes
"""

from typing import List

from fastapi import APIRouter

from ..schemas import CoursePublic

router = APIRouter(prefix="/api/public", tags=["Courses"])


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
            "name": "Engenharia de Computadores e Telemática",
            "short_code": "MECT",
            "color": "#FF5733",
        },
        {
            "id": 2,
            "name": "Engenharia Informática",
            "short_code": "LEI",
            "color": "#33FF57",
        },
        {
            "id": 3,
            "name": "Engenharia Eletrónica e Telecomunicações",
            "short_code": "MIEET",
            "color": "#3357FF",
        },
    ]
