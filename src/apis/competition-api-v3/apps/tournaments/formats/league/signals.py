from apps.matches.models import Match
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from ...models import TournamentCompetitor, TournamentFormat
from .models import LeagueStanding
from .service import LeagueFormat


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


@receiver(pre_delete, sender=Match)
def update_league_standings_on_match_delete(sender, instance: Match, **kwargs):
    """When a match is deleted in a league tournament, update the standings accordingly."""
    tournament = instance.tournament

    if tournament.tournament_format != TournamentFormat.LEAGUE:
        return

    league_tournament = LeagueFormat(tournament)

    league_tournament.delete_result(instance)
