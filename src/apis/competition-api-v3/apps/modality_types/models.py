import uuid
from typing import TYPE_CHECKING

from apps.seasons.models import Season
from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from apps.modalities.models import SeasonModality


class ModalityTypeModes(models.TextChoices):
    MODALITY = "modality", "Modality"
    POINTS = "points", "Points"


class ModalityTypeTournamentCompetitorTypes(models.TextChoices):
    TEAM = "team", "Team"
    INDIVIDUAL = "individual", "Individual"


class ModalityType(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    mode = models.CharField(max_length=20, choices=ModalityTypeModes.choices)
    tournament_competitor_type = models.CharField(
        max_length=20, choices=ModalityTypeTournamentCompetitorTypes.choices
    )

    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="modality_types"
    )

    # Related field type hints for IDEs and type checkers
    if TYPE_CHECKING:
        escaloes: RelatedManager["Escalao"]
        season_modalities: RelatedManager["SeasonModality"]

    def __str__(self):
        return self.name


class Escalao(models.Model):

    id = models.AutoField(primary_key=True)
    modality_type = models.ForeignKey(
        ModalityType, on_delete=models.CASCADE, related_name="escaloes"
    )

    name = models.CharField(max_length=255)
    min_participants = models.IntegerField(null=True, blank=True)
    max_participants = models.IntegerField(null=True, blank=True)

    points = models.JSONField(default=list)

    def __str__(self):
        return f"{self.modality_type.name} - {self.name}"
