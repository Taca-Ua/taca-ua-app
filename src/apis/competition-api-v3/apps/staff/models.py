import uuid

from django.db import models
from jsonschema import ValidationError


class Staff(models.Model):
    """Model representing a staff member."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    staff_number = models.CharField(max_length=64, unique=True, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)

    def clean(self):
        # Ensure that at least one of staff_number or contact is provided
        if not self.staff_number and not self.contact:
            raise ValidationError("Either staff_number or contact must be provided.")

    def __str__(self):
        return self.name
