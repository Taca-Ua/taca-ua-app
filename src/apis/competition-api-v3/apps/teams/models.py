import uuid
from typing import TYPE_CHECKING

from apps.athletes.models import Athlete
from apps.courses.models import Course
from apps.modalities.models import Modality
from apps.seasons.models import Season
from django.db import models


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    modality = models.ForeignKey(
        Modality, on_delete=models.CASCADE, related_name="teams"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="teams")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="teams")

    athletes = models.ManyToManyField(Athlete, related_name="teams")

    @property
    def logo_url(self):
        return self.course.nucleus.logo_url

    if TYPE_CHECKING:
        modality_id: uuid.UUID
        course_id: uuid.UUID
        season_id: int
