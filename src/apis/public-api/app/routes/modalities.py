"""
Modality routes
"""

from typing import List

from fastapi import APIRouter

from ..schemas import ModalityPublic

router = APIRouter(prefix="/api/public", tags=["Modalities"])


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
            "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
        },
        {
            "id": 2,
            "name": "Futsal",
            "type": "coletiva",
            "scoring_schema": {"win": 3, "draw": 1, "loss": 0},
        },
        {
            "id": 3,
            "name": "Andebol",
            "type": "coletiva",
            "scoring_schema": {"win": 2, "loss": 0},
        },
        {
            "id": 4,
            "name": "Voleibol",
            "type": "coletiva",
            "scoring_schema": {"win": 2, "loss": 0},
        },
    ]
