import uuid
from typing import TYPE_CHECKING, Union

from apps.athletes.models import Athlete
from apps.choices import TournamentCompetitorType, TournamentStatus
from apps.modalities.models import Modality
from apps.modality_types.models import ModalityType
from apps.seasons.models import Season
from apps.teams.models import Team
from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


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
        competitors: "RelatedManager[TournamentCompetitor]"


class TournamentCompetitor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="competitors"
    )

    # This can reference either an individual or a team based on the tournament's competitor_type
    competitor_id = models.UUIDField()

    class Meta:
        unique_together = ("tournament", "competitor_id")

    @property
    def competitor(self) -> Union[Athlete, Team]:
        if self.tournament.competitor_type == TournamentCompetitorType.INDIVIDUAL:
            return Athlete.objects.get(id=self.competitor_id)
        else:
            return Team.objects.get(id=self.competitor_id)


class TournamentResult(models.Model):
    competitor = models.OneToOneField(
        TournamentCompetitor, on_delete=models.CASCADE, related_name="result"
    )
    position = models.PositiveIntegerField()
