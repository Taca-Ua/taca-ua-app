import uuid
from typing import TYPE_CHECKING

from apps.athletes.models import Athlete
from apps.choices import TournamentCompetitorType, TournamentFormat, TournamentStatus
from apps.modalities.models import Modality
from apps.modality_types.models import ModalityType
from apps.seasons.models import Season
from apps.teams.models import Team
from django.db import models

if TYPE_CHECKING:
    from apps.matches.models import Match, MatchParticipant
    from apps.tournaments.models import TournamentCompetitor
    from django.db.models.manager import RelatedManager

    from .formats.league.models import LeagueSettings


class Tournament(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=TournamentStatus.choices, default=TournamentStatus.DRAFT
    )
    start_date = models.DateField()
    competitor_type = models.CharField(
        max_length=20, choices=TournamentCompetitorType.choices
    )
    tournament_format = models.CharField(
        max_length=20, choices=TournamentFormat.choices, default=TournamentFormat.FREE
    )

    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    scoring_format = models.ForeignKey(ModalityType, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    @property
    def rank(self):
        """Determine the tournament's rank based on the number of competitors and the scoring format's escaloes."""
        number_of_competitors = self.competitors.count()
        escaloes = self.scoring_format.escaloes.order_by("min_participants")
        for escaloes in escaloes:
            lower_bound = (
                escaloes.min_participants
                if escaloes.min_participants is not None
                else 0
            )
            upper_bound = (
                escaloes.max_participants
                if escaloes.max_participants is not None
                else float("inf")
            )

            if lower_bound <= number_of_competitors <= upper_bound:
                return escaloes.name

        return "Unranked"

    if TYPE_CHECKING:
        competitors: RelatedManager[TournamentCompetitor]
        matches: RelatedManager[Match]
        league_settings: LeagueSettings


class TournamentCompetitor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="competitors"
    )

    # This can reference either an individual or a team based on the tournament's competitor_type()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    athlete = models.ForeignKey(
        Athlete, on_delete=models.CASCADE, null=True, blank=True
    )

    if TYPE_CHECKING:
        match_participations: "RelatedManager['MatchParticipant']"

    @property
    def name(self):
        if self.tournament.competitor_type == TournamentCompetitorType.INDIVIDUAL:
            return self.athlete.name if self.athlete else "Unknown Athlete"
        elif self.tournament.competitor_type == TournamentCompetitorType.TEAM:
            return self.team.name if self.team else "Unknown Team"
        return "Unknown Competitor"

    @property
    def course_name(self):
        if self.tournament.competitor_type == TournamentCompetitorType.INDIVIDUAL:
            return (
                self.athlete.course.name
                if self.athlete and self.athlete.course
                else "Unknown Course"
            )
        elif self.tournament.competitor_type == TournamentCompetitorType.TEAM:
            return (
                self.team.course.name
                if self.team and self.team.course
                else "Unknown Course"
            )
        return "Unknown Course"

    @property
    def entity_id(self):
        if self.tournament.competitor_type == TournamentCompetitorType.INDIVIDUAL:
            return self.athlete.id if self.athlete else None
        elif self.tournament.competitor_type == TournamentCompetitorType.TEAM:
            return self.team.id if self.team else None
        return None

    @property
    def entity(self) -> Athlete | Team | None:
        if self.tournament.competitor_type == TournamentCompetitorType.INDIVIDUAL:
            return self.athlete
        elif self.tournament.competitor_type == TournamentCompetitorType.TEAM:
            return self.team
        return None

    class Meta:
        unique_together = ("tournament", "team", "athlete")


class TournamentResult(models.Model):
    competitor = models.OneToOneField(
        TournamentCompetitor, on_delete=models.CASCADE, related_name="result"
    )
    position = models.PositiveIntegerField()
