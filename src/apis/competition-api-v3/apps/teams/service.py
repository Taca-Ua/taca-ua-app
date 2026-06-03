from django.db import transaction

from .models import Team


@transaction.atomic
def create_team(name, modality_id, course_id, season_id) -> Team:

    team = Team.objects.create(
        name=name, modality_id=modality_id, course_id=course_id, season_id=season_id
    )

    return team


@transaction.atomic
def update_team(team_id, name=None) -> Team:
    team = Team.objects.get(id=team_id)

    if name is not None:
        team.name = name

    team.save()
    return team


@transaction.atomic
def delete_team(team_id) -> None:
    team = Team.objects.get(id=team_id)
    team.delete()


@transaction.atomic
def add_athletes_to_team(team_id, athlete_ids) -> Team:
    team = Team.objects.get(id=team_id)
    team.athletes.add(*athlete_ids)

    return team


@transaction.atomic
def remove_athletes_from_team(team_id, athlete_ids) -> Team:
    team = Team.objects.get(id=team_id)
    team.athletes.remove(*athlete_ids)

    return team
