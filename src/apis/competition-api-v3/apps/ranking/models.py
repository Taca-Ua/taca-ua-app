from typing import TYPE_CHECKING
from uuid import UUID

from apps.courses.models import Course
from apps.modalities.models import Modality
from apps.seasons.models import Season
from apps.tournaments.models import Tournament
from django.db import models


class CourseTournamentPosition(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    points = models.PositiveIntegerField()

    class Meta:
        unique_together = ("season", "course", "modality", "tournament")

    if TYPE_CHECKING:
        season_id: int
        modality_id: UUID
        course_id: UUID
        tournament_id: UUID


class RankingAmmendment(models.Model):
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="ranking_ammendments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="ranking_ammendments"
    )
    modality = models.ForeignKey(
        Modality,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ranking_ammendments",
    )

    points = models.IntegerField()
    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        season_id: int
        course_id: UUID
        modality_id: UUID | None
