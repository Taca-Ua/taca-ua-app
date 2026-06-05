from uuid import UUID

from django.db.models import QuerySet

from .formats import FormatRegistry
from .models import Tournament


def list_tournaments(
    status=None, modality_id=None, season_id=None
) -> QuerySet[Tournament]:
    """Retrieve a list of all tournaments."""
    queryset = Tournament.objects.all()

    if status is not None:
        queryset = queryset.filter(status=status)

    if modality_id is not None:
        queryset = queryset.filter(modality_id=modality_id)

    if season_id is not None:
        queryset = queryset.filter(season_id=season_id)

    return queryset


def get_tournament(tournament_id: UUID) -> QuerySet[Tournament]:
    """Retrieve a tournament by its ID."""
    tournament = Tournament.objects.filter(id=tournament_id)
    if not tournament.exists():
        raise Tournament.DoesNotExist(
            f"Tournament with id {tournament_id} does not exist."
        )

    return tournament.first()


def get_tournament_format_details(tournament_id: UUID) -> dict:
    tournament = get_tournament(tournament_id)
    format_engine = FormatRegistry.get_format(tournament)
    return format_engine.get_details()
