from apps.seasons.models import Season
from django.db.models.signals import post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


@receiver(post_save, sender=Season)
def season_post_save(sender, instance, created, **kwargs):
    """When a season is created or updated, request a projection update for the season."""
    request_projection_update(
        ProjectionUpdateRequestTypes.SEASON, {"season_id": str(instance.id)}
    )
