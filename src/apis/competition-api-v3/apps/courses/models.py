import uuid

from apps.nucleus.models import Nucleus
from apps.seasons.models import Season
from django.db import models


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=100)

    nucleus = models.ForeignKey(
        Nucleus, on_delete=models.CASCADE, related_name="courses"
    )
    seasons = models.ManyToManyField(Season, related_name="courses")

    def __str__(self):
        return f"<Course: {self.name} ({self.abbreviation})>"
