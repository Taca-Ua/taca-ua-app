import logging

from apps.tournaments.models import Tournament
from apps.tournaments.selectors import get_tournament_results
from django.db import transaction

from .models import CourseTournamentPosition

logger = logging.getLogger(__name__)


COURSE_MAX_AWARDS = (
    2  # Maximum number of courses that can receive points in a tournament
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
    for course_id, points in course_points_to_award.items():
        if points > 0:
            CourseTournamentPosition.objects.create(
                season_id=tournament.season_id,
                modality_id=tournament.modality_id,
                course_id=course_id,
                tournament_id=tournament.id,
                points=points,
            )


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
