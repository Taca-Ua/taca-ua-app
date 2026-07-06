from apps.choices import TournamentFormat
from rest_framework.exceptions import ValidationError

from ..models import Tournament
from .base import BaseFormat, MatchSuggestion
from .free.service import FreeFormat
from .league.service import LeagueFormat


class FormatRegistry:
    _engines: dict[str, BaseFormat] = {
        TournamentFormat.FREE: FreeFormat,
        TournamentFormat.LEAGUE: LeagueFormat,
    }

    @classmethod
    def register(cls, format_name, format_class):
        cls._engines[format_name] = format_class

    @classmethod
    def get_format(cls, tournament: Tournament) -> BaseFormat:
        engine_class = cls._engines.get(tournament.tournament_format)
        if not engine_class:
            raise ValidationError(
                f"No format engine registered for format: {tournament.tournament_format}"
            )

        return engine_class(tournament)


__all__ = ["FormatRegistry", "MatchSuggestion"]
