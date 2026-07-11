from uuid import UUID

from apps.athletes.selectors import get_athletes_table
from apps.athletes.service import update_athlete
from apps.courses.service import add_course_to_season
from apps.modalities.service import add_modality_to_season
from apps.modality_types.service import create_modality_type
from apps.teams.service import create_team
from django.db import transaction
from django.utils import timezone

from .models import Season
from .selectors import get_current_season


def _copy_modality_types_from_previous_season(
    previous_season: Season, new_season: Season
) -> dict[UUID, UUID]:
    """Copy modality types from the previous season to the new season."""

    modality_types_map = {}
    for prev_modality_type in previous_season.modality_types.all():
        new_modality_type = create_modality_type(
            name=prev_modality_type.name,
            mode=prev_modality_type.mode,
            tournament_competitor_type=prev_modality_type.tournament_competitor_type,
            description=prev_modality_type.description,
            season_id=new_season.id,
            escaloes_data=[
                {
                    "name": esc.name,
                    "min_participants": esc.min_participants,
                    "max_participants": esc.max_participants,
                    "points": esc.points,
                }
                for esc in prev_modality_type.escaloes.all()
            ],
        )
        modality_types_map[prev_modality_type.id] = new_modality_type.id

    return modality_types_map


def _associate_modalities_from_previous_season(
    previous_season: Season, new_season: Season, modality_types_map: dict[UUID, UUID]
):
    for prev_modality in previous_season.season_modalities.all():
        add_modality_to_season(
            modality_id=prev_modality.modality.id,
            season_id=new_season.id,
            modality_type_id=modality_types_map.get(prev_modality.modality_type.id),
        )


def _associate_courses_from_previous_season(
    previous_season: Season, new_season: Season
):
    for prev_course in previous_season.courses.all():
        add_course_to_season(course_id=prev_course.id, season_id=new_season.id)


def _copy_teams_from_previous_season(previous_season: Season, new_season: Season):
    for prev_team in previous_season.teams.all():
        create_team(
            name=prev_team.name,
            modality_id=prev_team.modality.id,
            course_id=prev_team.course.id,
            season_id=new_season.id,
        )


def _delete_athletes_docs_from_previous_season(previous_season: Season):
    athletes = get_athletes_table(has_docs=True)

    for athlete in athletes:
        update_athlete(
            athlete_id=athlete.id,
            course_proof_file=None,
            course_proof_deleted=True,
            payment_proof_file=None,
            payment_proof_deleted=True,
        )


@transaction.atomic
def create_season(name: str, admin_id: UUID) -> Season:

    # finish current season
    current_season = get_current_season()
    current_season.is_current = False
    current_season.finished_at = timezone.now()
    current_season.finished_by = str(admin_id)
    current_season.save()

    # create new season
    new_season = Season.objects.create(name=name, is_current=True)

    # new season will inherit modality types from previous season
    modality_types_map = _copy_modality_types_from_previous_season(
        previous_season=current_season, new_season=new_season
    )

    # new season will inherit associated modalities from previous season
    _associate_modalities_from_previous_season(
        previous_season=current_season,
        new_season=new_season,
        modality_types_map=modality_types_map,
    )

    # new season will inherit associated courses from previous season
    _associate_courses_from_previous_season(
        previous_season=current_season, new_season=new_season
    )

    # new season will inherit teams from previous season
    _copy_teams_from_previous_season(
        previous_season=current_season, new_season=new_season
    )

    # delete athletes docs from previous season
    _delete_athletes_docs_from_previous_season(previous_season=current_season)

    return new_season


@transaction.atomic
def create_initial_season(name: str):
    """
    Create the initial season if it doesn't exist.
    This function is intended to be called during the application startup.
    """
    if Season.objects.exists():
        return

    # create the initial season
    season = Season.objects.create(name=name, is_current=True)

    return season
