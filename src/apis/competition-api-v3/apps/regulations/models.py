from django.db import models
import uuid

from apps.seasons.models import Season
from apps.modalities.models import Modality


class Regulation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="regulations")
    modality = models.OneToOneField(Modality, on_delete=models.CASCADE, related_name="regulation", null=True, blank=True)

    def __str__(self):
        return f"<Regulation: {self.title}>"