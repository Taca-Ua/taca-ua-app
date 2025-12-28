"""
Service for communicating with ranking-service microservice
"""

import os
from typing import Any, Dict, List, Optional

from .base_service import BaseService


class RankingService(BaseService):
    """Service for managing rankings via ranking-service"""

    def __init__(self):
        base_url = os.environ.get("RANKING_SERVICE_URL", "http://ranking-service:8000")
        super().__init__(base_url)

    def recalculate_modality_ranking(
        self,
        modality_id: str,
        season_id: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Recalculate ranking for a modality

        Args:
            modality_id: UUID of the modality
            season_id: Optional season UUID (uses active season if not provided)
            force: Force recalculation even if up-to-date

        Returns:
            Recalculation result
        """
        data = {}

        if season_id:
            data["season_id"] = season_id
        if force:
            data["force"] = force

        return self.post(f"/rankings/modality/{modality_id}/recalculate", data)

    def recalculate_course_ranking(
        self,
        course_id: str,
        season_id: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Recalculate ranking for a course

        Args:
            course_id: UUID of the course
            season_id: Optional season UUID (uses active season if not provided)
            force: Force recalculation even if up-to-date

        Returns:
            Recalculation result
        """
        data = {}

        if season_id:
            data["season_id"] = season_id
        if force:
            data["force"] = force

        return self.post(f"/rankings/course/{course_id}/recalculate", data)

    def recalculate_general_ranking(
        self, season_id: Optional[str] = None, force: bool = False
    ) -> Dict[str, Any]:
        """
        Recalculate general ranking

        Args:
            season_id: Optional season UUID (uses active season if not provided)
            force: Force recalculation even if up-to-date

        Returns:
            Recalculation result
        """
        data = {}

        if season_id:
            data["season_id"] = season_id
        if force:
            data["force"] = force

        return self.post("/rankings/general/recalculate", data)

    def get_modality_ranking(
        self, modality_id: str, season_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get ranking for a modality

        Args:
            modality_id: UUID of the modality
            season_id: Optional season UUID

        Returns:
            List of rankings ordered by score
        """
        params = {}

        if season_id:
            params["season_id"] = season_id

        return self.get(f"/rankings/modality/{modality_id}", params=params)

    def get_course_ranking(
        self, course_id: str, season_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get ranking for a course across all modalities

        Args:
            course_id: UUID of the course
            season_id: Optional season UUID

        Returns:
            Course ranking data with scores per modality
        """
        params = {}

        if season_id:
            params["season_id"] = season_id

        return self.get(f"/rankings/course/{course_id}", params=params)

    def get_general_ranking(
        self, season_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get general ranking across all courses

        Args:
            season_id: Optional season UUID

        Returns:
            List of course rankings ordered by total score
        """
        params = {}

        if season_id:
            params["season_id"] = season_id

        return self.get("/rankings/general", params=params)

    def get_ranking_history(
        self,
        season_id: Optional[str] = None,
        course_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get historical rankings

        Args:
            season_id: Optional season UUID (returns all seasons if not provided)
            course_id: Optional course UUID to filter
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of historical rankings
        """
        params = {"limit": limit, "offset": offset}

        if season_id:
            params["season_id"] = season_id
        if course_id:
            params["course_id"] = course_id

        return self.get("/rankings/history", params=params)
