from abc import ABC, abstractmethod


class BaseFormat(ABC):
    def __init__(self, tournament):
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
