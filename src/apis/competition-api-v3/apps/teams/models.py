import uuid

from apps.athletes.models import Athlete
from apps.courses.models import Course
from apps.modalities.models import Modality
from apps.seasons.models import Season
from django.db import models


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    athletes = models.ManyToManyField(Athlete, related_name="teams")
