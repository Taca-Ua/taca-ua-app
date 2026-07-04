from abc import ABC, abstractmethod

from apps.matches.models import Match

from ..models import Tournament


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
