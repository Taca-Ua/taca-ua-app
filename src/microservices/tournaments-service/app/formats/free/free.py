from typing import Any, Dict

from app.formats.base import FormatEngine
from app.models import Tournament


class FreeFormatEngine(FormatEngine):
    """A simple format engine that does not enforce any specific structure on the tournament."""

    @property
    def format_name(self) -> str:
        return "free"

    def complete_tournament(self, tournament: Tournament, format_data: Dict[str, Any]):
        """Free format does not have specific completion logic, so we can simply return the tournament as is or perform any necessary finalization based on format_data."""
        return tournament

    def get_standings(self, db, tournament_id):
        return None
