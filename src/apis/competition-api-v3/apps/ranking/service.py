import logging
from uuid import UUID

from apps.tournaments.models import Tournament
from apps.tournaments.selectors import get_tournament_results
from django.db import transaction
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import RankingComputedV1
from taca_events.pydantic_schemas.ranking import (
    GeneralRankingEntryData,
    ModalityRankingEntryData,
    RankingComputedData,
)

from .models import CourseTournamentPosition
from .selectors import get_general_ranking

logger = logging.getLogger(__name__)


COURSE_MAX_AWARDS = (
    2  # Maximum number of courses that can receive points in a tournament
)


@transaction.atomic
def emit_updated_rankings_event(season_id: int):
    """Emits a RankingComputedV1 event with the latest general and modality rankings for the given season."""

    general_ranking = get_general_ranking(season_id)
    emit_schema_event(
        RankingComputedV1(
            data=RankingComputedData(
                season_id=season_id,
                general_ranking=[
                    GeneralRankingEntryData(
                        season_id=season_id,
                        course_id=entry.course.id,
                        points=entry.points,
                        tournaments_participated=0,
                    )
                    for entry in general_ranking
                ],
                modality_rankings=[
                    ModalityRankingEntryData(
                        season_id=entry.season_id,
                        modality_id=entry.modality_id,
                        course_id=entry.course_id,
                        points=entry.points,
                    )
                    for entry in CourseTournamentPosition.objects.filter(
                        season_id=season_id
                    )
                ],
            )
        ),
        aggregate_id=UUID(
            int=season_id
        ),  # Using season_id as part of the aggregate_id for scoping
    )


@transaction.atomic
def submit_tournament_results(
    tournament: Tournament, *, emit_computed_event: bool = True
):

    results = get_tournament_results(tournament.id)

    # delete existing CourseTournamentPosition entries for the tournament
    CourseTournamentPosition.objects.filter(tournament_id=tournament.id).delete()

    awarded_courses_count = {}
    course_points_to_award = {}
    for result in results:
        comp = result.competitor.entity.course
        escalao = tournament.rank

        if not escalao:
            raise ValueError(
                f"Tournament {tournament.id} does not have an associated rank."
            )

        points_to_award = (
            escalao.points[result.position - 1]
            if result.position <= len(escalao.points) and result.position > 0
            else 0
        )

        # init counter
        if comp.id not in awarded_courses_count:
            awarded_courses_count[comp.id] = 0

        # init points to award
        if comp.id not in course_points_to_award:
            course_points_to_award[comp.id] = 0

        if awarded_courses_count[comp.id] < COURSE_MAX_AWARDS:
            course_points_to_award[comp.id] += points_to_award
            awarded_courses_count[comp.id] += 1

    # Create CourseTournamentPosition entries for each course with awarded points
    changes_made = False
    for course_id, points in course_points_to_award.items():
        if points > 0:
            CourseTournamentPosition.objects.create(
                season_id=tournament.season_id,
                modality_id=tournament.modality_id,
                course_id=course_id,
                tournament_id=tournament.id,
                points=points,
            )
            changes_made = True

    if emit_computed_event and changes_made:
        # emit event with updated rankings after processing the tournament results
        emit_updated_rankings_event(tournament.season_id)


@transaction.atomic
def recompute_rankings(
    season_id: int = None,
    modality_id: int = None,
    course_id: int = None,
    tournament_id: int = None,
):
    """Recomputes the rankings for all tournaments in the given season and emits an event with the updated rankings."""

    logger.info(
        f"Recomputing rankings for season_id={season_id}, modality_id={modality_id}, course_id={course_id}, tournament_id={tournament_id}"
    )

    # Get all CourseTournamentPosition entries that match the given filters (season, modality, course)
    relevant_entries = CourseTournamentPosition.objects.all()

    if season_id is not None:
        relevant_entries = relevant_entries.filter(season_id=season_id)

    if modality_id is not None:
        relevant_entries = relevant_entries.filter(modality_id=modality_id)

    if course_id is not None:
        relevant_entries = relevant_entries.filter(course_id=course_id)

    if tournament_id is not None:
        relevant_entries = relevant_entries.filter(tournament_id=tournament_id)

    # Get the distinct tournament IDs from the relevant entries
    relevant_tournaments_ids = relevant_entries.values_list(
        "tournament_id", flat=True
    ).distinct()
    relevant_tournaments = Tournament.objects.filter(id__in=relevant_tournaments_ids)
    for tournament in relevant_tournaments:
        submit_tournament_results(tournament, emit_computed_event=False)

    # After recomputing the rankings for all relevant tournaments, emit an event for each affected season
    season_ids = relevant_entries.values_list("season_id", flat=True).distinct()
    for season_id in season_ids:
        emit_updated_rankings_event(season_id)
