from django.db import models
from django.db.models import QuerySet

from ..models import Team


def render_team_list(teams: QuerySet[Team]) -> QuerySet[Team]:
    return teams.select_related("modality", "course")


def render_team_detail(team: QuerySet[Team] | Team) -> QuerySet[Team]:

    if isinstance(team, Team):
        team = Team.objects.filter(id=team.id)

    team = render_team_list(team)

    team = team.annotate(logo_url=models.F("course__nucleus__logo_url"))

    team = team.select_related("season").prefetch_related("athletes")

    return team
