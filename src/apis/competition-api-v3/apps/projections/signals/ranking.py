from apps.courses.models import Course
from apps.nucleus.models import Nucleus
from apps.ranking.models import CourseTournamentPosition
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


@receiver(post_save, sender=CourseTournamentPosition)
def handle_course_tournament_position_save(
    sender, instance: CourseTournamentPosition, **kwargs
):
    # Trigger the projection update for the course and nucleus
    request_projection_update(
        ProjectionUpdateRequestTypes.GENERAL_RANKING,
        {"season_id": str(instance.season_id)},
    )
    request_projection_update(
        ProjectionUpdateRequestTypes.MODALITY_RANKING,
        {
            "season_id": str(instance.season_id),
            "modality_id": str(instance.modality_id),
        },
    )


@receiver([post_delete, post_save], sender=Course)
def handle_course_delete(sender, instance: Course, **kwargs):
    # Trigger the projection update for the course and nucleus
    request_projection_update(
        ProjectionUpdateRequestTypes.GENERAL_RANKING, {}, key="season_all"
    )
    request_projection_update(
        ProjectionUpdateRequestTypes.MODALITY_RANKING, {}, key="season_all_modality_all"
    )


@receiver([post_delete, post_save], sender=Nucleus)
def handle_nucleus_delete(sender, instance: Nucleus, **kwargs):
    # Trigger the projection update for the course and nucleus
    request_projection_update(
        ProjectionUpdateRequestTypes.GENERAL_RANKING, {}, key="season_all"
    )
    request_projection_update(
        ProjectionUpdateRequestTypes.MODALITY_RANKING, {}, key="season_all_modality_all"
    )
