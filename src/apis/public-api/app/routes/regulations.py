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
    description="Get a list of regulations with optional category filter",
)
async def list_regulations(
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """List regulations with optional category filter

    Returns regulations filtered by category (e.g., 'geral', 'futsal', 'futebol').
    If no category is provided, returns all regulations.
    """
    # Mock regulations database
    all_regulations = [
        {
            "id": 1,
            "title": "Regulamento Geral",
            "description": "Regulamento geral da Taça UA. Define as regras gerais, pontuação, e normas de conduta para todas as modalidades.",
            "category": "geral",
            "file_url": "/api/public/regulations/1/download",
            "created_at": datetime(2025, 1, 15, 10, 0),
            "updated_at": datetime(2025, 1, 15, 10, 0),
        },
        {
            "id": 2,
            "title": "Regulamento Futsal",
            "description": "Regulamento específico para a modalidade de Futsal. Inclui regras de jogo, composição de equipas, e critérios de desempate.",
            "category": "futsal",
            "file_url": "/api/public/regulations/2/download",
            "created_at": datetime(2025, 1, 20, 10, 0),
            "updated_at": datetime(2025, 1, 20, 10, 0),
        },
        {
            "id": 3,
            "title": "Regulamento Futebol",
            "description": "Regulamento específico para a modalidade de Futebol. Define as normas de participação e competição.",
            "category": "futebol",
            "file_url": "/api/public/regulations/3/download",
            "created_at": datetime(2025, 1, 25, 10, 0),
            "updated_at": datetime(2025, 1, 25, 10, 0),
        },
        {
            "id": 4,
            "title": "Regulamento Andebol",
            "description": "Regulamento específico para a modalidade de Andebol. Define as normas de participação e competição.",
            "category": "andebol",
            "file_url": "/api/public/regulations/4/download",
            "created_at": datetime(2025, 2, 1, 10, 0),
            "updated_at": datetime(2025, 2, 1, 10, 0),
        },
        {
            "id": 5,
            "title": "Regulamento Minecraft",
            "description": "Regulamento específico para o torneio de Minecraft. Define as regras do jogo, mapas permitidos, e critérios de vitória.",
            "category": "minecraft",
            "file_url": "/api/public/regulations/5/download",
            "created_at": datetime(2025, 2, 5, 10, 0),
            "updated_at": datetime(2025, 2, 5, 10, 0),
        },
    ]

    # Apply filter
    if category:
        filtered = [r for r in all_regulations if r.get("category") == category.lower()]
        return filtered

    return all_regulations


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
