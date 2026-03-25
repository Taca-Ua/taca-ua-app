"""
Service for communicating with ranking-service microservice

NOT IMPLEMENTED YET - RANKING SERVICE IS NOT READY
"""

import os
from dataclasses import dataclass
from typing import List

from ..utils.base_service import BaseService


@dataclass
class TournamentTierInfo:
    rank: str
    points: List[int]


class RankingService(BaseService):
    """Service for managing rankings via ranking-service"""

    def __init__(self):
        base_url = os.environ.get("RANKING_SERVICE_URL", "http://ranking-service:8000")
        super().__init__(base_url)

    def get_tournament_tier(self, tournament_id: str) -> TournamentTierInfo:
        """
        Get the tier of a tournament

        Args:
            tournament_id: UUID of the tournament

        Returns:
            Tier information for the tournament
        """
        tournament_tier_data = self.get(f"/rankings/tournament/{tournament_id}/tier")
        return TournamentTierInfo(**tournament_tier_data)

    def calculate_tournament_tier(
        self, tournament_id: str, participant_count: int, modality_type_id: str
    ) -> TournamentTierInfo:
        """
        Calculate the tier of a tournament based on participant count and modality type

        Args:
            tournament_id: UUID of the tournament
            participant_count: Number of participants in the tournament
            modality_type_id: ID of the modality type

        Returns:
            Calculated tier information for the tournament
        """
        calculation_data = {
            "tournament_id": tournament_id,
            "participant_count": participant_count,
            "modality_type_id": modality_type_id,
        }
        tournament_tier_data = self.post(
            "/rankings/calc-tournament-tier/", calculation_data
        )
        return TournamentTierInfo(**tournament_tier_data)


ranking_service_client = RankingService()
