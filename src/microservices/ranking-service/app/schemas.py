from typing import List

from pydantic import BaseModel


class TournamentTierResponse(BaseModel):
    rank: str
    points: List[int]


class TournamentTierCalculationRequest(BaseModel):
    tournament_id: str
    participant_count: int
    modality_type_id: str
