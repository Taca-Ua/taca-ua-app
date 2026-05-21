"""
Abstract base class for competition format engines.

Each format engine defines how tournaments progress through rounds,
generate match configurations, validate them, and calculate standings.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from app.models import Tournament, TournamentCompetitor
from requests import Session
from sqlalchemy import UUID
from taca_events.pydantic_schemas.matches import (
    MatchCreatedV1,
    MatchDeletedV1,
    MatchResultUpdatedV1,
)


@dataclass
class FormatStandings:
    competitor_id: str
    position: int
    format_meta: Dict[
        UUID, Any
    ]  # Format-specific metadata (e.g., points, wins, losses)


class FormatEngine(ABC):
    """
    Abstract base class for competition format engines.

    Each tournament format (league, playoff, bracket, etc.) implements
    this interface to define progression rules.
    """

    # Class-level registry of format engines
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Returns the format name (e.g., 'league', 'playoff')"""
        pass

    def complete_tournament(
        self, tournament: Tournament, format_data: Dict[str, Any]
    ) -> None:
        """
        Create a tournament with the given format and format-specific data.
        """
        pass

    def update_tournament(
        self, tournament: Tournament, format_data: Dict[str, Any]
    ) -> None:
        """
        Update a tournament's format-specific data.
        """
        pass

    def on_competitor_added(
        self, db: Session, tournament_competitor: TournamentCompetitor
    ) -> None:
        """
        Handle logic when a competitor is added to a tournament.
        This can be used to update format-specific data structures.
        """
        pass

    def on_competitor_removed(
        self, db: Session, tournament_competitor: TournamentCompetitor
    ) -> None:
        """
        Handle logic when a competitor is removed from a tournament.
        This can be used to update format-specific data structures.
        """
        pass

    # Event handler methods for routing events to format engines
    def event_handle_match_created(self, db: Session, event: MatchCreatedV1) -> None:
        """Handle match created event."""
        # This method can be used to route match created events to the appropriate format engine
        pass

    def event_handle_match_deleted(self, db: Session, event: MatchDeletedV1) -> None:
        """Handle match deleted event."""
        # This method can be used to route match deleted events to the appropriate format engine
        pass

    def event_handle_match_result_updated(
        self, db: Session, event: MatchResultUpdatedV1
    ) -> None:
        """Handle match result updated event."""
        # This method can be used to route match result updated events to the appropriate format engine
        pass

    # Utility method to convert format-specific data to a common structure for API responses
    @abstractmethod
    def get_standings(self, db: Session, tournament_id: UUID) -> List[FormatStandings]:
        """
        Get the current standings for a tournament in a format-agnostic way.
        This can be used to provide a consistent API response structure regardless of the format.
        """
        pass
