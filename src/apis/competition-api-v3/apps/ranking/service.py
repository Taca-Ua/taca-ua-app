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
    for course_id, points in course_points_to_award.items():
        if points > 0:
            CourseTournamentPosition.objects.create(
                season_id=tournament.season_id,
                modality_id=tournament.modality_id,
                course_id=course_id,
                tournament_id=tournament.id,
                points=points,
            )
