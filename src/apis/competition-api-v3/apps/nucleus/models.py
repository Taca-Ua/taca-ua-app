import uuid
from typing import TYPE_CHECKING

from apps.seasons.models import Season
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models

if TYPE_CHECKING:
    from apps.admins.models import Admin
    from apps.courses.models import Course
    from django.db.models.manager import RelatedManager


class Nucleus(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True, null=True)

    admins_ids = ArrayField(models.UUIDField(), default=list, blank=True)  # deprecated

    seasons = models.ManyToManyField(Season, related_name="nuclei")

    if TYPE_CHECKING:
        courses: RelatedManager["Course"]
        admins: RelatedManager["Admin"]

    class Meta:
        indexes = [
            GinIndex(fields=["admins_ids"]),
        ]

    def check_belongs_to_season(self, season: Season) -> bool:
        return self.seasons.filter(id=season.id).exists()

    def __str__(self):
        return f"<Nucleus {self.name} ({self.abbreviation})>"
