import uuid
from typing import TYPE_CHECKING

from apps.courses.models import Course
from django.db import models

if TYPE_CHECKING:
    from apps.teams.models import Team
    from django.db.models.manager import RelatedManager

class Athlete(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    student_number = models.CharField(max_length=64, unique=True)
    is_member = models.BooleanField(default=False)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="athletes")

    if TYPE_CHECKING:
        teams: RelatedManager[Team]

    def __str__(self):
        return self.name
