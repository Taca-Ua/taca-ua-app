from uuid import UUID

from django.db.models import Q, QuerySet

from .formats import FormatRegistry
from .models import Tournament


def get_tournaments_table(
    status=None, modality_id=None, season_id=None, admin_id: UUID = None
) -> QuerySet[Tournament]:

    queryset = Tournament.objects.all()

    if status is not None:
        queryset = queryset.filter(status=status)

    if modality_id is not None:
        queryset = queryset.filter(modality_id=modality_id)

    if season_id is not None:
        queryset = queryset.filter(season_id=season_id)

    if admin_id is not None:
        queryset = queryset.filter(
            Q(competitors__athlete__course__nucleus__admins__id=admin_id)
            | Q(competitors__team__course__nucleus__admins__id=admin_id)
        ).distinct()

    queryset = queryset.select_related("modality", "season", "scoring_format")

    return queryset


def get_tournament_by_id(tournament_id: UUID) -> Tournament:
    tournament_qs = get_tournaments_table().filter(id=tournament_id)

    tournament_qs = tournament_qs.prefetch_related(
        "competitors__athlete__course",
        "competitors__team__course",
    )
    return tournament_qs.get()


def get_tournament_format_details(tournament_id: UUID) -> dict:
    tournament = get_tournament_by_id(tournament_id)
    format_engine = FormatRegistry.get_format(tournament)
    return format_engine.get_details()
