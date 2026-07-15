from uuid import UUID

from apps.choices import ModalityTypeModes
from apps.matches.selectors import get_matches_table
from django.db import models
from django.db.models import Count, ExpressionWrapper, Q, QuerySet, Value

from .models import Athlete


def get_athletes_table(
    admin_id: UUID = None,
    course_id: UUID = None,
    athlete_id: UUID = None,
    nucleus_id: UUID = None,
    team_id: UUID = None,
    has_docs: bool = None,
) -> QuerySet[Athlete]:
    queryset = Athlete.objects.all()

    if admin_id:
        queryset = queryset.filter(course__nucleus__admins__id=admin_id).distinct()

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if athlete_id:
        queryset = queryset.filter(id=athlete_id)

    if team_id:
        queryset = queryset.filter(teams__id=team_id)

    if nucleus_id:
        queryset = queryset.filter(course__nucleus_id=nucleus_id)

    if has_docs is not None and has_docs:
        queryset = queryset.filter(
            Q(course_proof_file_url__isnull=False)
            | Q(payment_proof_file_url__isnull=False)
        )

    queryset = queryset.select_related("course")
    return queryset


def get_athlete_by_id(athlete_id: UUID) -> Athlete:

    athlete_qs = get_athletes_table().filter(id=athlete_id)

    return athlete_qs.get()


def get_athletes_stats_for_team(team_id: UUID) -> QuerySet[Athlete]:

    matches = get_matches_table(
        team_id=team_id,
        tournament_scoring_type=ModalityTypeModes.MODALITY,  # only matches from tournaments with scoring type of the modality
    )
    total_matches = matches.count()
    athletes = get_athletes_table(team_id=team_id)

    # annotate athletes with participation percentage
    if total_matches == 0:
        athletes = athletes.annotate(
            participation_percentage=Value(0.0, output_field=models.FloatField()),
        )
    else:
        athletes = athletes.annotate(
            participation_percentage=ExpressionWrapper(
                Count(
                    "match_lineups",
                    distinct=True,
                    filter=Q(match_lineups__match_participant__match__in=matches),
                )
                * 100.0
                / total_matches,
                output_field=models.FloatField(),
            )
        )

    return athletes
