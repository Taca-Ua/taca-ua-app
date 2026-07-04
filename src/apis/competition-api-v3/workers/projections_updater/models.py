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
    HOME_PAGE_CONFIG = "home_page_config", "Home Page Config"


class ProjectionUpdateRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PROCESSED = "processed", "Processed"

    projection_type = models.CharField(
        max_length=255, choices=ProjectionUpdateRequestTypes.choices
    )
    payload = models.JSONField()
    key = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["projection_type", "key"],
                condition=models.Q(status__in=["pending", "processing"]),
                name="unique_projection_update_request",
            )
        ]
