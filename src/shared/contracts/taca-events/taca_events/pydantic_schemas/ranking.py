"""
Typed Pydantic event schemas for the Ranking Service.
"""

from typing import List
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema

# ================================================================== #
# Data payload models
# ================================================================== #


class GeneralRankingEntryData(BaseModel):
    """Points earned by a single course across all modalities."""

    season_id: int
    course_id: UUID
    points: int
    tournaments_participated: int = 0


class ModalityRankingEntryData(BaseModel):
    """Points earned by a single course within a specific modality."""

    season_id: int
    modality_id: UUID
    course_id: UUID
    points: int


class RankingComputedData(BaseModel):
    """Payload emitted whenever all ranking tables are recomputed."""

    season_id: int
    general_ranking: List[GeneralRankingEntryData] = []
    modality_rankings: List[ModalityRankingEntryData] = []


# ================================================================== #
# EventSchema subclasses
# ================================================================== #


class RankingComputedV1(EventSchema):
    data: RankingComputedData

    @classmethod
    def event_type(cls) -> str:
        return "ranking.computed.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "ranking"
