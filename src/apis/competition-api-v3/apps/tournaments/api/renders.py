from django.db.models import Prefetch, QuerySet

from ..models import Tournament, TournamentCompetitor


# Renderers
def render_tournaments(tournaments: QuerySet[Tournament]) -> QuerySet[Tournament]:
    """Render a list of tournaments for API response."""

    # modality is singular so we can use select_related for an efficient join
    tournaments = tournaments.select_related("modality")
    return tournaments


def render_tournament_detail(
    tournament: QuerySet[Tournament] | Tournament,
) -> QuerySet[Tournament]:
    """Render a single tournament with detailed information for API response."""

    if isinstance(tournament, Tournament):
        tournament = Tournament.objects.filter(id=tournament.id)

    # render the with the lower level
    tournament = render_tournaments(tournament)

    # season and scoring format are singular so we can use select_related for an efficient join
    tournament = tournament.select_related("season", "scoring_format")

    # annotate competitors with their data based on the tournament's competitor type
    tournament = tournament.prefetch_related(
        Prefetch(
            "competitors",
            queryset=TournamentCompetitor.objects.select_related(
                "athlete__course", "team__course"
            ),
        ),
    )

    return tournament
