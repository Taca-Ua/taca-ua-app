"""
Regulation routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import RegulationPublic

router = APIRouter(prefix="/api/public", tags=["Regulations"])


@router.get(
    "/regulations",
    response_model=List[RegulationPublic],
    summary="List regulations",
    description="Get a list of regulations with optional filters",
)
async def list_regulations(
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
):
    """List regulations with optional filters

    Returns regulations filtered by modality_id.
    If no filters are provided, returns all regulations.
    """
    # Mock regulations database
    # modality_id: 1=Futebol, 2=Futsal, 3=Andebol, None=Geral
    all_regulations = [
        {
            "id": 1,
            "title": "Regulamento Geral",
            "description": "Regulamento geral da Taça UA. Define as regras gerais, pontuação, e normas de conduta para todas as modalidades.",
            "modality_id": None,
            "file_url": "/api/public/regulations/1/download",
            "created_at": datetime(2025, 1, 15, 10, 0),
        },
        {
            "id": 2,
            "title": "Regulamento Futsal",
            "description": "Regulamento específico para a modalidade de Futsal. Inclui regras de jogo, composição de equipas, e critérios de desempate.",
            "modality_id": 2,
            "file_url": "/api/public/regulations/2/download",
            "created_at": datetime(2025, 1, 20, 10, 0),
        },
        {
            "id": 3,
            "title": "Regulamento Futebol",
            "description": "Regulamento específico para a modalidade de Futebol. Define as normas de participação e competição.",
            "modality_id": 1,
            "file_url": "/api/public/regulations/3/download",
            "created_at": datetime(2025, 1, 25, 10, 0),
        },
        {
            "id": 4,
            "title": "Regulamento Andebol",
            "description": "Regulamento específico para a modalidade de Andebol. Define as normas de participação e competição.",
            "modality_id": 3,
            "file_url": "/api/public/regulations/4/download",
            "created_at": datetime(2025, 2, 1, 10, 0),
        },
    ]

    # Apply filters
    filtered = all_regulations
    if modality_id is not None:
        filtered = [r for r in filtered if r.get("modality_id") == modality_id]

    return filtered


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
