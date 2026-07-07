from apps.courses.models import Course
from apps.nucleus.models import Nucleus
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


# Direct changes to Course instances
@receiver(post_save, sender=Course)
def course_post_save(sender, instance: Course, **kwargs):
    """When a course is created or updated, request a projection update for that course."""
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.COURSE,
        payload={"course_id": str(instance.id)},
    )


@receiver(post_delete, sender=Course)
def course_post_delete(sender, instance: Course, **kwargs):
    """When a course is deleted, request a projection update for that course."""
    request_projection_update(
        projection_type=ProjectionUpdateRequestTypes.COURSE,
        payload={"course_id": str(instance.id)},
    )


# Changes to related models that affect Course projections
@receiver(post_save, sender=Nucleus)
def nucleus_post_save(sender, instance: Nucleus, created: bool, **kwargs):
    """When a nucleus is updated, request a projection update for all courses in that nucleus."""
    if not created:
        request_projection_update(
            projection_type=ProjectionUpdateRequestTypes.COURSE,
            payload={"nucleus_id": str(instance.id)},
        )
