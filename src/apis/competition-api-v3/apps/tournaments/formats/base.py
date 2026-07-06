import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from apps.matches.models import Match

from ..models import Tournament


@dataclass
class MatchSuggestion:
    competitors_ids: list[uuid.UUID]
    format_specific_data: dict


class BaseFormat(ABC):
    def __init__(self, tournament: Tournament):
        self.tournament = tournament

    @abstractmethod
    def create(self, format_data) -> dict:
        pass

    @abstractmethod
    def update(self, format_data) -> dict:
        pass

    @abstractmethod
    def get_details(self) -> dict:
        pass

    @abstractmethod
    def record_result(self, match: Match) -> dict:
        pass

    @abstractmethod
    def suggest_matches(self, configuration: dict) -> list[MatchSuggestion]:
        pass

    @abstractmethod
    def generate_matches(self, matches_configuration: list[MatchSuggestion]) -> None:
        pass
