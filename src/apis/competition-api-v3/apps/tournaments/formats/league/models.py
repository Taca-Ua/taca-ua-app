from django.db import models

from ...models import Tournament, TournamentCompetitor


class DrawRule(models.TextChoices):
    GOAL_DIFFERENCE = "GOAL_DIFFERENCE", "Goal Difference"
    GOALS_SCORED = "GOALS_SCORED", "Goals Scored"


class LeagueSettings(models.Model):
    """Settings specific to league format tournaments."""

    tournament = models.OneToOneField(
        Tournament, on_delete=models.CASCADE, primary_key=True
    )

    win_points = models.PositiveIntegerField(default=3)
    draw_points = models.PositiveIntegerField(default=1)
    loss_points = models.PositiveIntegerField(default=0)

    draw_rule = models.CharField(
        max_length=255, choices=DrawRule.choices, blank=True, null=True
    )


class LeagueStanding(models.Model):
    """Materialized view to represent the current standings in a league tournament."""

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    competitor = models.ForeignKey(TournamentCompetitor, on_delete=models.CASCADE)

    played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)

    points_for = models.PositiveIntegerField(default=0)
    points_against = models.PositiveIntegerField(default=0)

    league_points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("tournament", "competitor")
