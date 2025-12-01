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
            "description": "Futebol de 11",
        },
        {"id": 2, "name": "Futsal", "type": "coletiva", "description": "Futsal de 5"},
        {
            "id": 3,
            "name": "Ténis",
            "type": "individual",
            "description": "Ténis individual",
        },
    ]
