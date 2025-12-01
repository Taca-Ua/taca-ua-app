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
