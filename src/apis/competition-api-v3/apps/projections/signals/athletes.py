from apps.athletes.models import Athlete
from apps.courses.models import Course
from apps.nucleus.models import Nucleus
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


# Direct changes to Athlete instances
@receiver(post_save, sender=Athlete)
def athlete_post_save(sender, instance: Athlete, created, **kwargs):
    """When an athlete is created or updated, request a projection update for that athlete."""
    request_projection_update(
        ProjectionUpdateRequestTypes.ATHLETE, {"athlete_id": str(instance.id)}
    )


@receiver(post_delete, sender=Athlete)
def athlete_post_delete(sender, instance: Athlete, **kwargs):
    """When an athlete is deleted, request a projection update for that athlete."""
    request_projection_update(
        ProjectionUpdateRequestTypes.ATHLETE, {"athlete_id": str(instance.id)}
    )


@receiver(m2m_changed, sender=Athlete.teams.through)
def athlete_teams_changed(sender, instance, action, reverse, pk_set, **kwargs):
    """When an athlete's teams are changed, request a projection update for that athlete."""
    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    athlete_ids = set()
    if reverse:
        # instance is an Athlete
        athlete_ids = {instance.id}
    else:
        # instance is a Team, pk_set contains athlete IDs
        athlete_ids = pk_set

    for athlete_id in athlete_ids:
        request_projection_update(
            ProjectionUpdateRequestTypes.ATHLETE, {"athlete_id": str(athlete_id)}
        )


# Changes to related models that affect Athlete projections
@receiver(post_save, sender=Course)
def course_post_save(sender, instance: Course, created, **kwargs):
    """When a course is updated, request a projection update for all athletes in that course."""

    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.ATHLETE, {"course_id": str(instance.id)}
    )


@receiver(post_save, sender=Nucleus)
def nucleus_post_save(sender, instance: Nucleus, created, **kwargs):
    """When a nucleus is updated, request a projection update for all athletes in that nucleus."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.ATHLETE, {"nucleus_id": str(instance.id)}
    )
