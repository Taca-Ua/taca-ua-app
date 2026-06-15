from uuid import UUID

from apps.seasons.selectors import get_current_season
from django.db import transaction
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas import (
    TeamCreatedV1,
    TeamDeletedV1,
    TeamPlayerAddedV1,
    TeamPlayerRemovedV1,
    TeamUpdatedV1,
)
from taca_events.pydantic_schemas.teams import (
    TeamCreatedData,
    TeamDeletedData,
    TeamPlayerAddedData,
    TeamPlayerRemovedData,
    TeamUpdatedData,
)

from .models import Team


@transaction.atomic
def create_team(
    name: str, modality_id: UUID, course_id: UUID, season_id: int = None
) -> Team:

    if season_id is None:
        season = get_current_season()
        if season is None:
            raise ValueError("No active season found. Please specify a season_id.")
        season_id = season.id

    team = Team.objects.create(
        name=name, modality_id=modality_id, course_id=course_id, season_id=season_id
    )

    # emit event to OutboxTable
    emit_schema_event(
        event=TeamCreatedV1(
            data=TeamCreatedData(
                team_id=team.id,
                name=team.name,
                modality_id=team.modality_id,
                course_id=team.course_id,
                season_id=team.season_id,
            )
        ),
        aggregate_id=team.id,
    )

    return team


@transaction.atomic
def update_team(team_id, name=None) -> Team:
    team = Team.objects.get(id=team_id)

    if name is not None:
        team.name = name

    team.save()

    # emit event to OutboxTable
    emit_schema_event(
        event=TeamUpdatedV1(
            data=TeamUpdatedData(
                team_id=team.id,
                name=team.name,
                modality_id=team.modality_id,
                course_id=team.course_id,
            )
        ),
        aggregate_id=team.id,
    )

    return team


@transaction.atomic
def delete_team(team_id) -> None:
    team = Team.objects.get(id=team_id)

    # emit event to OutboxTable
    emit_schema_event(
        event=TeamDeletedV1(
            data=TeamDeletedData(
                team_id=team.id,
            )
        ),
        aggregate_id=team.id,
    )

    team.delete()


@transaction.atomic
def add_athletes_to_team(team_id, athlete_ids) -> Team:
    team = Team.objects.get(id=team_id)
    team.athletes.add(*athlete_ids)

    # emit event to OutboxTable for each athlete added
    for athlete_id in athlete_ids:
        emit_schema_event(
            event=TeamPlayerAddedV1(
                data=TeamPlayerAddedData(
                    team_id=team.id,
                    student_id=athlete_id,
                )
            ),
            aggregate_id=team.id,
        )

    return team


@transaction.atomic
def remove_athletes_from_team(team_id, athlete_ids) -> Team:
    team = Team.objects.get(id=team_id)
    team.athletes.remove(*athlete_ids)

    # emit event to OutboxTable for each athlete removed
    for athlete_id in athlete_ids:
        emit_schema_event(
            event=TeamPlayerRemovedV1(
                data=TeamPlayerRemovedData(
                    team_id=team.id,
                    student_id=athlete_id,
                )
            ),
            aggregate_id=team.id,
        )

    return team
