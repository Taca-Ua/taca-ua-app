from django.db.models import QuerySet

from .models import Team


def get_teams_table(season_id=None, modality_id=None, course_id=None) -> QuerySet[Team]:
    queryset = Team.objects.all()

    if season_id is not None:
        queryset = queryset.filter(season_id=season_id)

    if modality_id is not None:
        queryset = queryset.filter(modality_id=modality_id)

    if course_id is not None:
        queryset = queryset.filter(course_id=course_id)

    queryset = queryset.select_related("modality", "course__nucleus")

    return queryset


def get_team_by_id(team_id) -> Team:
    team_qs = get_teams_table().filter(id=team_id)

    team_qs = team_qs.select_related("season").prefetch_related("athletes")

    return team_qs.get()
