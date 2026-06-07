from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from ...models import TournamentCompetitor, TournamentFormat
from .models import LeagueStanding


@receiver(post_save, sender=TournamentCompetitor)
def update_league_standings(sender, instance: TournamentCompetitor, created, **kwargs):
    """When a competitor is added to a league tournament, create an initial standing for them."""
    if created and instance.tournament.tournament_format == TournamentFormat.LEAGUE:
        LeagueStanding.objects.create(
            competitor=instance,
            points=0,
            wins=0,
            draws=0,
            losses=0,
        )


@receiver(pre_delete, sender=TournamentCompetitor)
def delete_league_standing(sender, instance: TournamentCompetitor, **kwargs):
    """When a competitor is removed from a league tournament, delete their standing."""
    try:
        standing = LeagueStanding.objects.get(competitor=instance)
        standing.delete()
    except LeagueStanding.DoesNotExist:
        pass
