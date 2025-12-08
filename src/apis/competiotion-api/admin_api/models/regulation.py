"""
Django model for Regulation
"""

from django.db import models


class Regulation(models.Model):
    """
    Model to store regulation documents
    """

    title = models.CharField(max_length=255, help_text="Title of the regulation")

    description = models.TextField(
        blank=True, default="", help_text="Description of the regulation"
    )

    modality = models.ForeignKey(
        "modalities.Modality",
        on_delete=models.CASCADE,
        related_name="regulations",
        help_text="Sport modality this regulation applies to",
    )

    # File storage fields
    file_url = models.URLField(
        max_length=500, help_text="URL to access the file in MinIO"
    )

    file_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="SHA256 hash of the file content (ensures uniqueness)",
    )

    file_size = models.PositiveIntegerField(help_text="File size in bytes")

    file_name = models.CharField(max_length=255, help_text="Original filename")

    content_type = models.CharField(
        max_length=100,
        default="application/pdf",
        help_text="MIME type of the file",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_regulations",
        help_text="User who uploaded this regulation",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this regulation is currently active"
    )

    version = models.PositiveIntegerField(
        default=1, help_text="Version number of this regulation"
    )

    class Meta:
        db_table = "regulations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["modality", "-created_at"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"

    @property
    def file_size_mb(self):
        """Return file size in megabytes"""
        return round(self.file_size / (1024 * 1024), 2)

    def deactivate(self):
        """Mark this regulation as inactive"""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])
