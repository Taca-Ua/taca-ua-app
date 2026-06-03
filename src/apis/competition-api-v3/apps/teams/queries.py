from django.db.models import QuerySet

from .models import Team


def list_teams(season_id=None, modality_id=None, course_id=None) -> QuerySet[Team]:
    queryset = Team.objects.all()

    if season_id is not None:
        queryset = queryset.filter(season_id=season_id)

    if modality_id is not None:
        queryset = queryset.filter(modality_id=modality_id)

    if course_id is not None:
        queryset = queryset.filter(course_id=course_id)

    return queryset


def get_team(team_id) -> QuerySet[Team]:

    queryset = Team.objects.filter(id=team_id)
    if not queryset.exists():
        raise Team.DoesNotExist(f"Team with id {team_id} does not exist.")

    return queryset
