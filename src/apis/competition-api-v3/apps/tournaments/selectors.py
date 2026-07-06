from uuid import UUID

from django.db.models import Q, QuerySet

from .formats import FormatRegistry, MatchSuggestion
from .models import Tournament, TournamentResult


def get_tournaments_table(
    status=None,
    modality_id=None,
    season_id=None,
    modality_type_id=None,
    tournament_id=None,
    team_id: UUID = None,
    athlete_id: UUID = None,
    admin_id: UUID = None,
    course_id: UUID = None,
) -> QuerySet[Tournament]:

    queryset = Tournament.objects.all()

    if status is not None:
        queryset = queryset.filter(status=status)

    if modality_id is not None:
        queryset = queryset.filter(modality_id=modality_id)

    if season_id is not None:
        queryset = queryset.filter(season_id=season_id)

    if modality_type_id is not None:
        queryset = queryset.filter(scoring_format_id=modality_type_id)

    if tournament_id is not None:
        queryset = queryset.filter(id=tournament_id)

    if admin_id is not None:
        queryset = queryset.filter(
            Q(competitors__athlete__course__nucleus__admins__id=admin_id)
            | Q(competitors__team__course__nucleus__admins__id=admin_id)
        ).distinct()

    if team_id is not None:
        queryset = queryset.filter(competitors__team__id=team_id).distinct()

    if athlete_id is not None:
        queryset = queryset.filter(competitors__athlete__id=athlete_id).distinct()

    if course_id is not None:
        queryset = queryset.filter(
            Q(competitors__athlete__course__id=course_id)
            | Q(competitors__team__course__id=course_id)
        ).distinct()

    queryset = queryset.select_related("modality", "season", "scoring_format")

    return queryset


def get_tournament_by_id(tournament_id: UUID) -> Tournament:
    tournament_qs = get_tournaments_table().filter(id=tournament_id)

    tournament_qs = tournament_qs.prefetch_related(
        "competitors__athlete__course",
        "competitors__team__course",
        "qualification_sources__tournament_target__modality",
    )
    return tournament_qs.get()


def get_tournament_format_details(tournament_id: UUID) -> dict:
    tournament = get_tournament_by_id(tournament_id)
    format_engine = FormatRegistry.get_format(tournament)
    return format_engine.get_details()


def get_tournament_results(tournament_id: UUID) -> QuerySet[TournamentResult]:

    results_qs = TournamentResult.objects.filter(
        competitor__tournament_id=tournament_id
    ).select_related(
        "competitor__athlete__course",
        "competitor__team__course",
    )
    results_qs = results_qs.order_by("position")

    return results_qs


def get_tournament_matches_suggestions(
    tournament_id: UUID, configuration: dict
) -> MatchSuggestion:
    tournament = get_tournament_by_id(tournament_id)

    format_engine = FormatRegistry.get_format(tournament)
    return format_engine.suggest_matches(configuration=configuration)
