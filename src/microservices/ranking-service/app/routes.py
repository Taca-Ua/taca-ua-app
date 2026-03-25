from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import schemas
from .database import get_db_session
from .logger import logger
from .models import ModalityTypeEscalao, Tournament, TournamentCompetitor

router = APIRouter()


def _find_escalao(
    escaloes: List[ModalityTypeEscalao], participant_count: int
) -> Optional[ModalityTypeEscalao]:
    """Return the escalao whose participant range covers *participant_count*."""
    for escalao in escaloes:
        if (
            escalao.min_participants is not None
            and participant_count < escalao.min_participants
        ):
            continue
        if (
            escalao.max_participants is not None
            and participant_count > escalao.max_participants
        ):
            continue
        return escalao
    return None


@router.get(
    "/rankings/tournament/{tournament_id}/tier",
    response_model=schemas.TournamentTierResponse,
)
def get_tournament_tier(tournament_id: UUID, db: Session = Depends(get_db_session)):
    """Get the tier of a tournament based on its number of participants."""
    # Fetch tournament details from the database
    tournament = (
        db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
    )
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # Count the number of competitors in the tournament
    participant_count = (
        db.query(TournamentCompetitor)
        .filter(TournamentCompetitor.tournament_id == tournament_id)
        .count()
    )
    escaloes = (
        db.query(ModalityTypeEscalao)
        .filter(ModalityTypeEscalao.modality_type_id == tournament.scoring_format_id)
        .all()
    )

    escalao = _find_escalao(escaloes, participant_count)
    if not escalao:
        logger.warning(
            f"No matching escalao found for tournament {tournament_id} with {participant_count} participants"
        )
        return schemas.TournamentTierResponse(
            rank="Unranked",
            points=[],
        )

    return schemas.TournamentTierResponse(
        rank=escalao.name,
        points=escalao.points,
    )


@router.post(
    "/rankings/calc-tournament-tier/", response_model=schemas.TournamentTierResponse
)
def calculate_tournament_tier(
    calc_data: schemas.TournamentTierCalculationRequest,
    db: Session = Depends(get_db_session),
):
    """Calculate the tier of a tournament based on a given number of participants and modality type."""
    escaloes = (
        db.query(ModalityTypeEscalao)
        .filter(ModalityTypeEscalao.modality_type_id == calc_data.modality_type_id)
        .all()
    )

    escalao = _find_escalao(escaloes, calc_data.participant_count)
    if not escalao:
        logger.warning(
            f"No matching escalao found for modality type {calc_data.modality_type_id} with {calc_data.participant_count} participants"
        )
        return schemas.TournamentTierResponse(
            rank="Unranked",
            points=[],
        )

    return schemas.TournamentTierResponse(
        rank=escalao.name,
        points=escalao.points,
    )
