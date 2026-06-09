import uuid
from typing import TYPE_CHECKING

from apps.nucleus.models import Nucleus
from apps.seasons.models import Season
from django.db import models

if TYPE_CHECKING:
    from apps.athletes.models import Athlete
    from django.db.models.manager import RelatedManager


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=100)

    nucleus = models.ForeignKey(
        Nucleus, on_delete=models.CASCADE, related_name="courses"
    )
    seasons = models.ManyToManyField(Season, related_name="courses")

    if TYPE_CHECKING:
        athletes: RelatedManager["Athlete"]

    @property
    def logo_url(self) -> str | None:
        return self.nucleus.logo_url if self.nucleus else None

    def __str__(self):
        return f"<Course: {self.name} ({self.abbreviation})>"
