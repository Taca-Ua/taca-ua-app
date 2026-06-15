from datetime import datetime
from typing import List
from uuid import UUID

from apps.matches.models import Match
from apps.modality_types.models import ModalityType, ModalityTypeModes
from apps.seasons.selectors import get_current_season
from django.db import transaction
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import (
    TournamentCompetitorAddedV1,
    TournamentCompetitorDeletedV1,
    TournamentCreatedV1,
    TournamentDeletedV1,
    TournamentFinishedV1,
    TournamentUpdatedV1,
)
from taca_events.pydantic_schemas.tournaments import (
    RankingEntryData,
    TournamentCompetitorAddedData,
    TournamentCompetitorDeletedData,
    TournamentCreatedData,
    TournamentDeletedData,
    TournamentFinishedData,
    TournamentUpdatedData,
)

from .formats import FormatRegistry
from .models import (
    Tournament,
    TournamentCompetitor,
    TournamentCompetitorType,
    TournamentResult,
    TournamentStatus,
)


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

    # emit event to OutboxTable
    emit_schema_event(
        event=TournamentCreatedV1(
            data=TournamentCreatedData(
                tournament_id=tournament.id,
                modality_id=tournament.modality_id,
                name=tournament.name,
                start_date=tournament.start_date.isoformat(),
                status=tournament.status,
                scoring_format_id=tournament.scoring_format_id,
                season_id=tournament.season_id,
                format_type=tournament.tournament_format,
            )
        ),
        aggregate_id=tournament.id,
    )

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

    # emit event to OutboxTable
    emit_schema_event(
        event=TournamentUpdatedV1(
            data=TournamentUpdatedData(
                tournament_id=tournament.id,
                name=tournament.name,
                start_date=(
                    tournament.start_date.isoformat() if tournament.start_date else None
                ),
                status=tournament.status,
                scoring_format_id=tournament.scoring_format_id,
            )
        ),
        aggregate_id=tournament.id,
    )
    return tournament


@transaction.atomic
def delete_tournament(tournament_id: UUID) -> None:
    tournament = Tournament.objects.get(id=tournament_id)

    # emit event to OutboxTable
    emit_schema_event(
        event=TournamentDeletedV1(
            data=TournamentDeletedData(
                tournament_id=tournament.id,
            )
        ),
        aggregate_id=tournament.id,
    )

    tournament.delete()


@transaction.atomic
def add_competitors_to_tournament(
    tournament_id: UUID, competitor_ids: list[UUID]
) -> Tournament:

    tournament = Tournament.objects.get(id=tournament_id)

    for competitor_id in competitor_ids:
        tourn_competitor = TournamentCompetitor.objects.create(
            tournament=tournament,
            team_id=(
                competitor_id
                if tournament.competitor_type == TournamentCompetitorType.TEAM
                else None
            ),
            athlete_id=(
                competitor_id
                if tournament.competitor_type == TournamentCompetitorType.INDIVIDUAL
                else None
            ),
        )

        # emit event to OutboxTable
        emit_schema_event(
            event=TournamentCompetitorAddedV1(
                data=TournamentCompetitorAddedData(
                    tournament_id=tournament.id,
                    competitor_id=tourn_competitor.id,
                    competitor_type=tournament.competitor_type,
                    competitor_entity_id=tourn_competitor.entity_id,
                    competitor_course_id=(
                        tourn_competitor.entity.course_id
                        if tourn_competitor.entity
                        else None
                    ),
                )
            ),
            aggregate_id=tournament.id,
        )

    return tournament


@transaction.atomic
def remove_competitors_from_tournament(
    tournament_id: UUID, competitor_ids: list[UUID]
) -> Tournament:
    tournament = Tournament.objects.get(id=tournament_id)

    competitors_to_remove = TournamentCompetitor.objects.filter(
        tournament=tournament, id__in=competitor_ids
    )

    # emit event to OutboxTable
    for competitor in competitors_to_remove:
        emit_schema_event(
            event=TournamentCompetitorDeletedV1(
                data=TournamentCompetitorDeletedData(
                    tournament_id=tournament.id,
                    competitor_id=competitor.id,
                    competitor_entity_id=competitor.entity_id,
                )
            ),
            aggregate_id=tournament.id,
        )

    competitors_to_remove.delete()
    return tournament


@transaction.atomic
def record_tournament_result(tournament_id: UUID, ranking_entries: list) -> Tournament:
    tournament = Tournament.objects.get(id=tournament_id)

    # clear existing results
    TournamentResult.objects.filter(competitor__tournament=tournament).delete()

    # record new results
    results: List[TournamentResult] = []
    for entry in ranking_entries:
        comp_result = TournamentResult.objects.create(
            competitor=TournamentCompetitor.objects.get(id=entry["competitor_id"]),
            position=entry["position"],
        )
        results.append(comp_result)

    # emit event to OutboxTable
    emit_schema_event(
        event=TournamentFinishedV1(
            data=TournamentFinishedData(
                tournament_id=tournament.id,
                ranking_entries=[
                    RankingEntryData(
                        competitor_id=result.competitor.id,
                        position=result.position,
                    )
                    for result in results
                ],
            )
        ),
        aggregate_id=tournament.id,
    )

    return tournament


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


@transaction.atomic
def tournament_format_match_result(match: Match) -> None:

    format_engine = FormatRegistry.get_format(match.tournament)
    if format_engine is None:
        raise ValueError(
            f"Unsupported tournament format: {match.tournament.tournament_format}"
        )

    format_engine.record_result(match)
