from dataclasses import dataclass

from apps.athletes.models import Athlete
from apps.matches.models import Match, MatchStatus
from apps.staff.models import Staff
from apps.tournaments.models import Tournament, TournamentStatus
from django.db.models import Count, Q, QuerySet

from .models import Season


@dataclass
class SeasonSummaryDTO:
    id: int
    name: str
    modality_types_count: int
    active_modalities_count: int
    active_courses_count: int
    teams_count: int
    tournaments_summary: dict
    matches_summary: dict
    members_summary: dict


def get_seasons_table() -> QuerySet[Season]:
    return Season.objects.all()


def get_season_by_id(season_id: int) -> Season:
    season_qs = get_seasons_table().filter(id=season_id)
    return season_qs.get()


def get_current_season() -> Season:
    season_qs = get_seasons_table()

    current_season = season_qs.filter(is_current=True)

    if not current_season.exists():
        raise Season.DoesNotExist("No current season found.")
    if current_season.count() > 1:
        raise Season.MultipleObjectsReturned("Multiple current seasons found.")

    return current_season.get()


def get_season_summary_by_id(season_id: int) -> SeasonSummaryDTO:
    season = get_season_by_id(season_id)

    modality_types_count = season.modality_types.distinct().count()
    active_modalities_count = season.season_modalities.distinct().count()
    active_courses_count = season.courses.distinct().count()
    teams_count = season.teams.distinct().count()

    tournaments_summary = Tournament.objects.filter(season_id=season_id).aggregate(
        finished=Count("id", filter=Q(status=TournamentStatus.FINISHED)),
        ongoing=Count("id", filter=Q(status=TournamentStatus.ACTIVE)),
        scheduled=Count("id", filter=Q(status=TournamentStatus.DRAFT)),
    )

    matches_summary = Match.objects.filter(tournament__season_id=season_id).aggregate(
        finished=Count("id", filter=Q(status=MatchStatus.FINISHED)),
        ongoing=Count("id", filter=Q(status=MatchStatus.IN_PROGRESS)),
        scheduled=Count("id", filter=Q(status=MatchStatus.SCHEDULED)),
    )

    members_summary = {
        "athletes": Athlete.objects.count(),
        "staff": Staff.objects.count(),
    }

    return SeasonSummaryDTO(
        id=season.id,
        name=season.name,
        modality_types_count=modality_types_count,
        active_modalities_count=active_modalities_count,
        active_courses_count=active_courses_count,
        teams_count=teams_count,
        tournaments_summary=tournaments_summary,
        matches_summary=matches_summary,
        members_summary=members_summary,
    )
