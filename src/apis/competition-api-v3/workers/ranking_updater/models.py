from django.db import models


class RankingRecomputationRequest(models.Model):
    season_id = models.UUIDField(null=True, blank=True)
    modality_id = models.UUIDField(null=True, blank=True)
    modality_type_id = models.UUIDField(null=True, blank=True)
    tournament_id = models.UUIDField(null=True, blank=True)

    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]
