from datetime import datetime
from uuid import UUID

from apps.modality_types.models import ModalityType, ModalityTypeModes
from apps.seasons.service import get_current_season
from django.db import transaction

from .formats import FormatRegistry
from .models import Tournament, TournamentCompetitor, TournamentStatus


@transaction.atomic
def create_tournament(
    name: str,
    modality_id: UUID,
    start_date: datetime = None,
    season_id: int = None,
    scoring_format_id: UUID = None,
    format: str = None,
    format_data: dict = None,
) -> Tournament:

    # if season_id is not provided, use the current season
    if season_id is None:
        season_id = get_current_season().id

    # if start_date is not provided, use the current date
    if start_date is None:
        start_date = datetime.now()

    # inherit competitor type from modality's modality type for the given season
    inherited_modality_type = ModalityType.objects.get(
        season_id=season_id, season_modalities__modality_id=modality_id
    )

    if scoring_format_id is None or scoring_format_id == inherited_modality_type.id:
        scoring_format_id = inherited_modality_type.id
    else:
        scoring_format = ModalityType.objects.get(id=scoring_format_id)

        # validate that the provided scoring format is in the same season as the tournament
        if scoring_format.season.id != season_id:
            raise ValueError(
                "Scoring format must be in the same season as the tournament."
            )

        # validate that the provided scoring format is of points type
        if scoring_format.mode != ModalityTypeModes.POINTS:
            raise ValueError("Scoring format must be of points type.")

    # create the tournament
    tournament = Tournament.objects.create(
        name=name,
        start_date=start_date,
        competitor_type=inherited_modality_type.tournament_competitor_type,
        modality_id=modality_id,
        scoring_format_id=scoring_format_id,
        season_id=season_id,
        tournament_format=format,
    )

    # initialize the tournament format engine
    format_engine = FormatRegistry.get_format(tournament)
    if format_engine is None:
        raise ValueError(
            f"Unsupported tournament format: {tournament.tournament_format}"
        )
    format_engine.create(format_data or {})

    return tournament


@transaction.atomic
def update_tournament(
    tournament_id: UUID,
    name: str = None,
    start_date: datetime = None,
    status: TournamentStatus = None,
) -> Tournament:
    tournament = Tournament.objects.get(id=tournament_id)

    if name is not None:
        tournament.name = name

    if start_date is not None:
        tournament.start_date = start_date

    if status is not None:
        tournament.status = status

    tournament.save()
    return tournament


@transaction.atomic
def delete_tournament(tournament_id: UUID) -> None:
    tournament = Tournament.objects.get(id=tournament_id)
    tournament.delete()


@transaction.atomic
def add_competitors_to_tournament(
    tournament_id: UUID, competitor_ids: list[UUID]
) -> Tournament:

    tournament = Tournament.objects.get(id=tournament_id)

    for competitor_id in competitor_ids:
        TournamentCompetitor.objects.create(
            tournament=tournament, competitor_id=competitor_id
        )

    return tournament


@transaction.atomic
def remove_competitors_from_tournament(
    tournament_id: UUID, competitor_ids: list[UUID]
) -> Tournament:
    tournament = Tournament.objects.get(id=tournament_id)

    TournamentCompetitor.objects.filter(
        tournament=tournament, id__in=competitor_ids
    ).delete()

    return tournament


@transaction.atomic
def record_tournament_result() -> Tournament:
    pass


@transaction.atomic
def update_tournament_format(tournament_id: UUID, format_data: dict) -> dict:
    tournament = Tournament.objects.get(id=tournament_id)
    if tournament is None:
        raise ValueError(f"Tournament with id {tournament_id} does not exist.")

    # re-initialize the tournament format engine with the new format and data
    format_engine = FormatRegistry.get_format(tournament)
    if format_engine is None:
        raise ValueError(
            f"Unsupported tournament format: {tournament.tournament_format}"
        )

    details = format_engine.update(format_data)

    return details
