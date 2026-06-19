from apps.athletes.models import Athlete
from apps.courses.models import Course
from apps.modalities.models import Modality
from apps.nucleus.models import Nucleus
from apps.teams.models import Team
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


# Direct changes to Team instances
@receiver(post_save, sender=Team)
def team_post_save_handler(sender, instance, created, **kwargs):
    """When a Team instance is created or updated, trigger a projection update request for the team."""

    # Trigger a projection update request for the team
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.TEAM,
        payload={"team_id": str(instance.id)},
    )


@receiver(m2m_changed, sender=Team.athletes.through)
def team_athletes_m2m_changed_handler(sender, instance, action, **kwargs):
    """When the athletes of a Team instance are changed, trigger a projection update request for the team."""

    if action in ["post_add", "post_remove", "post_clear"]:
        # Trigger a projection update request for the team
        request_projection_update(
            projection_type=ProjectionUpdateRequestTypes.TEAM,
            payload={"team_id": str(instance.id)},
        )


@receiver(post_delete, sender=Team)
def team_post_delete_handler(sender, instance, **kwargs):
    """When a Team instance is deleted, trigger a projection update request for the team."""
    # Trigger a projection update request for the team
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.TEAM,
        payload={"team_id": str(instance.id)},
    )


# Changes to related models that affect Team projections
@receiver(post_save, sender=Course)
def course_post_save_handler(sender, instance, created, **kwargs):
    """When a Course instance is updated, trigger a projection update request for the teams associated with the course."""

    if created:
        return

    # Trigger a projection update request for the courses teams
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.TEAM,
        payload={"course_id": str(instance.id)},
    )


@receiver(post_save, sender=Modality)
def modality_post_save_handler(sender, instance, created, **kwargs):
    """When a Modality instance is created or updated, trigger a projection update request for the modality."""

    if created:
        return

    # Trigger a projection update request for the modality teams
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.TEAM,
        payload={"modality_id": str(instance.id)},
    )


@receiver(post_save, sender=Nucleus)
def nucleus_post_save_handler(sender, instance, created, **kwargs):
    """When a Nucleus instance is created or updated, trigger a projection update request for the nucleus."""

    if created:
        return

    # Trigger a projection update request for the nucleus teams
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.TEAM,
        payload={"nucleus_id": str(instance.id)},
    )


@receiver(post_save, sender=Athlete)
def athlete_post_save_handler(sender, instance, created, **kwargs):
    """When an Athlete instance is created or updated, trigger a projection update request for the athlete's teams."""

    if created:
        return

    # Trigger a projection update request for the athlete teams
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.TEAM,
        payload={"athlete_id": str(instance.id)},
    )


@receiver(pre_delete, sender=Athlete)
def athlete_pre_delete_handler(sender, instance: Athlete, **kwargs):
    """When an Athlete instance is deleted, trigger a projection update request for the athlete's teams."""

    # Trigger a projection update request for the athlete teams
    for team in instance.teams.all():
        request_projection_update(
            projection_type=ProjectionUpdateRequestTypes.TEAM,
            payload={"team_id": str(team.id)},
        )
