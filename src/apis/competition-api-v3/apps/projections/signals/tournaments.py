from apps.athletes.models import Athlete
from apps.matches.models import Match
from apps.modalities.models import Modality
from apps.teams.models import Team
from apps.tournaments.formats.league.models import LeagueSettings, LeagueStanding
from apps.tournaments.models import Tournament, TournamentCompetitor, TournamentResult
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from workers.projections_updater.service import (
    ProjectionUpdateRequestTypes,
    request_projection_update,
)


@receiver([post_save, post_delete], sender=Tournament)
def tournament_post_save(sender, instance, **kwargs):
    """When a tournament is created or updated, trigger an update for the tournament projection."""
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT, {"tournament_id": str(instance.id)}
    )


@receiver([post_save, pre_delete], sender=TournamentCompetitor)
def tournament_competitor_post_save(sender, instance: TournamentCompetitor, **kwargs):
    """When a tournament competitor is created or updated, trigger an update for the tournament standings projection."""
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT,
        {"tournament_id": str(instance.tournament_id)},
    )
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT_STANDING,
        {"tournament_id": str(instance.tournament_id)},
    )


@receiver([post_save, pre_delete], sender=TournamentResult)
def tournament_result_post_save(sender, instance: TournamentResult, **kwargs):
    """When a tournament result is created or updated, trigger an update for the tournament standings projection."""
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT,
        {"tournament_id": str(instance.competitor.tournament_id)},
    )
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT_STANDING,
        {"tournament_id": str(instance.competitor.tournament_id)},
    )


@receiver(post_save, sender=Match)
def match_post_save(sender, instance, created, **kwargs):
    """When a match is created, trigger an update for the related tournaments projections."""
    if not created:
        return
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT,
        {"tournament_id": str(instance.tournament_id)},
    )


@receiver(pre_delete, sender=Match)
def match_pre_delete(sender, instance, **kwargs):
    """When a match is deleted, trigger an update for the related tournaments projections."""
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT,
        {"tournament_id": str(instance.tournament_id)},
    )
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT_STANDING,
        {"tournament_id": str(instance.tournament_id)},
    )


@receiver(post_save, sender=Modality)
def modality_post_save(sender, instance, created, **kwargs):
    """When a modality is updated, trigger an update for the related tournaments projections."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT, {"modality_id": str(instance.id)}
    )


@receiver(post_save, sender=Athlete)
def athlete_post_save(sender, instance, created, **kwargs):
    """When an athlete is updated, trigger an update for the related tournaments projections."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT_STANDING,
        {"athlete_id": str(instance.id)},
    )


@receiver(post_save, sender=Team)
def team_post_save(sender, instance, created, **kwargs):
    """When a team is updated, trigger an update for the related tournaments projections."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT_STANDING, {"team_id": str(instance.id)}
    )


# Format Signals
@receiver([post_save, post_delete], sender=LeagueStanding)
def league_standing_post_save(sender, instance: LeagueStanding, **kwargs):
    """When a league standing is created, updated or deleted, trigger an update for the related tournaments projections."""
    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT_STANDING,
        {"tournament_id": str(instance.competitor.tournament_id)},
    )


@receiver(post_save, sender=LeagueSettings)
def league_settings_post_save(sender, instance: LeagueSettings, created, **kwargs):
    """When a league settings is updated, trigger an update for the related tournaments projections."""
    if created:
        return

    request_projection_update(
        ProjectionUpdateRequestTypes.TOURNAMENT_STANDING,
        {"tournament_id": str(instance.tournament_id)},
    )
