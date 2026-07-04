from apps.nucleus.models import Nucleus
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


# Direct changes to Match instances
@receiver(post_save, sender=Nucleus)
def nucleus_post_save(sender, instance, created, **kwargs):
    """When a Nucleus is created or updated, we need to update the projections that depend on it."""
    request_projection_update(
        ProjectionUpdateRequestTypes.NUCLEO, {"nucleus_id": str(instance.id)}
    )


@receiver(post_delete, sender=Nucleus)
def nucleus_post_delete(sender, instance, **kwargs):
    """When a Nucleus is deleted, we need to update the projections that depend on it."""
    request_projection_update(
        ProjectionUpdateRequestTypes.NUCLEO, {"nucleus_id": str(instance.id)}
    )
