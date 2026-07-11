from apps.matches.models import Match
from django.db import models

from ...models import Tournament, TournamentCompetitor


class LeagueSettings(models.Model):
    """Settings specific to league format tournaments."""

    tournament = models.OneToOneField(
        Tournament,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="league_settings",
    )

    win_points = models.PositiveIntegerField(default=3)
    draw_points = models.PositiveIntegerField(default=1)
    loss_points = models.PositiveIntegerField(default=0)


class LeagueStanding(models.Model):
    """Materialized view to represent the current standings in a league tournament."""

    competitor = models.OneToOneField(
        TournamentCompetitor, on_delete=models.CASCADE, primary_key=True
    )

    points = models.PositiveIntegerField(default=0)
    played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    points_for = models.PositiveIntegerField(default=0)
    points_against = models.PositiveIntegerField(default=0)

    league_points = models.PositiveIntegerField(default=0)


class LeagueMatch(models.Model):
    """Represents a match in a league tournament."""

    match = models.OneToOneField(
        Match, on_delete=models.CASCADE, primary_key=True, related_name="league_match"
    )

    round_number = models.PositiveIntegerField()

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the league match."""
        return {
            "round_number": self.round_number,
        }
