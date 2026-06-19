from apps.athletes.models import Athlete
from apps.matches.models import Match
from apps.modalities.models import Modality
from apps.teams.models import Team
from apps.tournaments.models import Tournament
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


# Direct changes to Match instances
@receiver(post_save, sender=Match)
def match_post_save(sender, instance: Match, created, **kwargs):
    """When a match is created or updated, request a projection update for that match."""
    request_projection_update(
        ProjectionUpdateRequestTypes.MATCH, {"match_id": str(instance.id)}
    )


@receiver(post_delete, sender=Match)
def match_post_delete(sender, instance: Match, **kwargs):
    """When a match is deleted, request a projection update for that match."""
    request_projection_update(
        ProjectionUpdateRequestTypes.MATCH, {"match_id": str(instance.id)}
    )


# Changes to related models that affect Athlete projections
@receiver(post_save, sender=Tournament)
def tournament_post_save(sender, instance: Tournament, created, **kwargs):
    """When a tournament is updated, request a projection update for its matches."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.MATCH, {"tournament_id": str(instance.id)}
    )


@receiver(post_save, sender=Modality)
def modality_post_save(sender, instance: Modality, created, **kwargs):
    """When a modality is updated, request a projection update for its matches."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.MATCH, {"modality_id": str(instance.id)}
    )


@receiver(post_save, sender=Athlete)
def athlete_post_save(sender, instance: Athlete, created, **kwargs):
    """When an athlete is updated, request a projection update for matches involving that athlete."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.MATCH, {"athlete_id": str(instance.id)}
    )


@receiver(post_save, sender=Team)
def team_post_save(sender, instance: Team, created, **kwargs):
    """When a team is updated, request a projection update for matches involving that team."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.MATCH, {"team_id": str(instance.id)}
    )
