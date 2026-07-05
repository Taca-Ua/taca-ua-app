import logging
from datetime import datetime
from typing import List
from uuid import UUID

from apps.matches.models import Match
from apps.modality_types.models import ModalityType, ModalityTypeModes
from apps.ranking.service import submit_tournament_results
from apps.seasons.selectors import get_current_season
from django.db import transaction

from .formats import FormatRegistry, MatchSuggestion
from .models import (
    QualificationSlot,
    Tournament,
    TournamentCompetitor,
    TournamentCompetitorType,
    TournamentResult,
    TournamentStatus,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def create_tournament(
    name: str,
    modality_id: UUID,
    start_date: datetime = None,
    season_id: int = None,
    scoring_format_id: UUID = None,
    format: str = None,
    format_data: dict = None,
    competitor_rules: list[dict] = None,
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

    # add qualifying slots for competitors if provided
    if competitor_rules:
        for rule in competitor_rules:
            tournament_source = Tournament.objects.get(id=rule["tournament_id"])
            if tournament_source.season_id != season_id:
                raise ValueError(
                    "Competitor rules must be from tournaments in the same season."
                )
            if tournament == tournament_source:
                raise ValueError(
                    "Cannot add competitor rules from the same tournament."
                )

            if tournament_source.status == TournamentStatus.FINISHED:
                # if the source tournament is finished, add competitors directly to the new tournament
                add_competitors_to_tournament(
                    tournament_id=tournament.id,
                    competitor_ids=[
                        result.competitor.entity_id
                        for result in TournamentResult.objects.filter(
                            competitor__tournament=tournament_source,
                            position__gte=rule["starting_position"],
                            position__lte=rule["ending_position"],
                        )
                    ],
                )
            else:
                # if the source tournament is not finished, create a qualification slot for future competitors
                QualificationSlot.objects.create(
                    tournament_target=tournament,
                    tournament_source=tournament_source,
                    starting_position=rule["starting_position"],
                    ending_position=rule["ending_position"],
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

    if tournament.status == TournamentStatus.FINISHED:
        raise ValueError("Cannot add competitors to a finished tournament.")

    for competitor_id in competitor_ids:
        if TournamentCompetitor.objects.filter(
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
        ).exists():
            logger.warning(
                f"Competitor with id {competitor_id} already exists in tournament {tournament_id}. Skipping."
            )
            continue  # skip if competitor already exists in the tournament

        TournamentCompetitor.objects.create(
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

    return tournament


@transaction.atomic
def remove_competitors_from_tournament(
    tournament_id: UUID, competitor_ids: list[UUID]
) -> Tournament:
    tournament = Tournament.objects.get(id=tournament_id)

    if tournament.status == TournamentStatus.FINISHED:
        raise ValueError("Cannot remove competitors from a finished tournament.")

    competitors_to_remove = TournamentCompetitor.objects.filter(
        tournament=tournament, id__in=competitor_ids
    )

    competitors_to_remove.delete()
    return tournament


@transaction.atomic
def finish_tournament(tournament_id: UUID, ranking_entries: list) -> Tournament:
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

    tournament.status = TournamentStatus.FINISHED
    tournament.save()

    # fill qualification slots
    for slot in tournament.qualification_sources.all():
        add_competitors_to_tournament(
            tournament_id=slot.tournament_target.id,
            competitor_ids=[
                result.competitor.entity_id
                for result in TournamentResult.objects.filter(
                    competitor__tournament=slot.tournament_source,
                    position__gte=slot.starting_position,
                    position__lte=slot.ending_position,
                )
            ],
        )
        slot.delete()

    # submit tournament results to ranking service
    submit_tournament_results(tournament)

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


@transaction.atomic
def tournament_format_generate_matches(
    tournament_id: UUID, configuration: list[dict]
) -> None:
    tournament = Tournament.objects.get(id=tournament_id)
    if tournament is None:
        raise ValueError(f"Tournament with id {tournament_id} does not exist.")

    format_engine = FormatRegistry.get_format(tournament)
    if format_engine is None:
        raise ValueError(
            f"Unsupported tournament format: {tournament.tournament_format}"
        )

    format_engine.generate_matches(
        [
            MatchSuggestion(
                competitors_ids=match["competitors_ids"],
                format_specific_data=match.get("format_specific_data", {}),
            )
            for match in configuration
        ]
    )
