from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from apps.modality_types.models import ModalityType
from apps.seasons.models import Season
from django.db import models

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from apps.regulations.models import Regulation

class Modality(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    if TYPE_CHECKING:
        modality_seasons: RelatedManager[SeasonModality]
        regulation: RelatedManager[Regulation]

    def __str__(self):
        return self.name


class SeasonModality(models.Model):
    """Helper model to link Season, Modality and ModalityType"""

    id = models.AutoField(primary_key=True)

    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="season_modalities"
    )
    modality = models.ForeignKey(
        Modality, on_delete=models.CASCADE, related_name="modality_seasons"
    )
    modality_type = models.ForeignKey(
        ModalityType, on_delete=models.CASCADE, related_name="season_modalities"
    )

    class Meta:
        unique_together = ("season", "modality", "modality_type")

    def __str__(self):
        return f"{self.season.name} - {self.modality.name}"
