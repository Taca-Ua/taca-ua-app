from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from apps.modalities.models import SeasonModality
    from apps.modality_types.models import ModalityType
    from django.db.models.manager import RelatedManager


class Season(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_current = models.BooleanField(default=False, db_index=True)
    start_date = models.DateField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    finished_by = models.CharField(max_length=255, null=True, blank=True)

    # Related field type hint for IDEs and type checkers
    if TYPE_CHECKING:
        modality_types: RelatedManager[ModalityType]
        season_modalities: RelatedManager[SeasonModality]

    def __str__(self):
        return self.name
