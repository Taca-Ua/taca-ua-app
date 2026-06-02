import uuid

from apps.courses.models import Course
from django.db import models


class Athlete(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    student_number = models.CharField(max_length=64, unique=True)
    is_member = models.BooleanField(default=False)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
