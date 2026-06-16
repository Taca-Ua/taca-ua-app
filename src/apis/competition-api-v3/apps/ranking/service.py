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
def submit_tournament_results(tournament: Tournament):

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
            escalao.points[result.position]
            if result.position < len(escalao.points)
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

    if changes_made:
        # emit event with updated rankings after processing the tournament results
        emit_updated_rankings_event(tournament.season_id)
