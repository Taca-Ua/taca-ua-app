from apps.regulations.models import Regulation
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


@receiver([post_save, post_delete], sender=Regulation)
def regulation_post_save(sender, instance, **kwargs):
    """When a regulation is created, updated or deleted, request a projection update."""
    request_projection_update(
        ProjectionUpdateRequestTypes.REGULATION, {"regulation_id": str(instance.id)}
    )
