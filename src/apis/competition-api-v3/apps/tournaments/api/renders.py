from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Q, QuerySet
from django.db.models.functions import JSONObject

from ..models import Tournament, TournamentCompetitorType


# Helper functions
def competitor_data_annotation(
    tournament_queryset: QuerySet[Tournament],
) -> QuerySet[Tournament]:
    """Helper function to create an array of JSON objects for competitors based on tournament type."""

    tournament_competitor_type = tournament_queryset.values("competitor_type").first()[
        "competitor_type"
    ]

    field_name = None
    if tournament_competitor_type == TournamentCompetitorType.INDIVIDUAL:
        field_name = "athlete"
    elif tournament_competitor_type == TournamentCompetitorType.TEAM:
        field_name = "team"
    else:
        raise ValueError(
            f"Invalid tournament competitor type: '{tournament_competitor_type}'"
        )

    # Annotate tournament with array of competitor JSON objects
    tournament_queryset = tournament_queryset.annotate(
        competitors_data=ArrayAgg(
            JSONObject(
                id=F("competitors__id"),
                entity_id=F(f"competitors__{field_name}__id"),
                name=F(f"competitors__{field_name}__name"),
                course_name=F(f"competitors__{field_name}__course__name"),
            ),
            distinct=True,
            filter=Q(competitors__isnull=False),
        )
    )

    return tournament_queryset


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
    tournament = competitor_data_annotation(tournament)

    return tournament
