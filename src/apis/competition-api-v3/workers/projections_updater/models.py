from django.db import models


class ProjectionUpdateRequestTypes(models.TextChoices):
    TEAM = "team", "Team"
    ATHLETE = "athlete", "Athlete"
    TOURNAMENT = "tournament", "Tournament"
    MATCH = "match", "Match"
    TOURNAMENT_STANDING = "tournament_standing", "Tournament Standing"
    GENERAL_RANKING = "general_ranking", "General Ranking"
    MODALITY_RANKING = "modality_ranking", "Modality Ranking"
    NUCLEO = "nucleo", "Nucleo"
    SEASON = "season", "Season"
    REGULATION = "regulation", "Regulation"


class ProjectionUpdateRequest(models.Model):

    projection_type = models.CharField(
        max_length=255, choices=ProjectionUpdateRequestTypes.choices
    )
    payload = models.JSONField()

    processed = models.BooleanField(default=False)
