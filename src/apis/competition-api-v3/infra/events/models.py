import uuid

from django.db import models
from django.utils import timezone


class OutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=255, db_index=True)
    aggregate_type = models.CharField(max_length=100, db_index=True)
    aggregate_id = models.UUIDField(db_index=True)
    payload = models.JSONField()
    published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["published", "created_at"]),
            models.Index(fields=["event_type", "published"]),
            models.Index(fields=["aggregate_type", "aggregate_id"]),
        ]
        ordering = ["-created_at"]

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": str(self.aggregate_id),
            "payload": self.payload,
            "published": self.published,
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "retry_count": self.retry_count,
            "last_error": self.last_error,
        }

    def mark_as_published(self):
        """Mark this event as published."""
        self.published = True
        self.published_at = timezone.now()
        self.save(update_fields=["published", "published_at", "updated_at"])

    def record_error(self, error_message: str):
        """Record an error and increment retry count."""
        self.retry_count += 1
        self.last_error = error_message
        self.save(update_fields=["retry_count", "last_error", "updated_at"])

    def __repr__(self) -> str:
        return (
            f"<OutboxEvent id={self.id} event_type={self.event_type!r} "
            f"published={self.published}>"
        )

    def __str__(self) -> str:
        return f"{self.event_type} ({self.id})"
