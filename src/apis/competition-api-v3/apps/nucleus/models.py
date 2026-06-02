import uuid

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Nucleus(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True, null=True)

    admins_ids = ArrayField(models.UUIDField(), default=list, blank=True)

    class Meta:
        indexes = [
            GinIndex(fields=["admins_ids"]),
        ]

    def __str__(self):
        return f"<Nucleus {self.name} ({self.abbreviation})>"
