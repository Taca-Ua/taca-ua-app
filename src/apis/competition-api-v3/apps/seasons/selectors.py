from dataclasses import dataclass
from uuid import UUID

from apps.athletes.selectors import get_athletes_table
from apps.courses.selectors import get_courses_table
from apps.matches.models import Match
from apps.matches.selectors import get_matches_table
from apps.staff.selectors import get_staff_table
from apps.teams.selectors import get_teams_table
from apps.tournaments.models import TournamentStatus
from apps.tournaments.selectors import get_tournaments_table
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


def get_seasons_table(season_id: int = None) -> QuerySet[Season]:
    queryset = Season.objects.all()
    if season_id is not None:
        queryset = queryset.filter(id=season_id)

    return queryset


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


def get_season_summary_by_id(season_id: int, admin_id: UUID) -> SeasonSummaryDTO:
    season = get_season_by_id(season_id)

    modality_types_qs = season.modality_types

    active_modalities_qs = season.season_modalities

    active_courses_qs = get_courses_table(season_id=season_id, admin_id=admin_id)

    teams_qs = get_teams_table(season_id=season_id, admin_id=admin_id)

    tournaments_summary = get_tournaments_table(
        season_id=season_id, admin_id=admin_id
    ).aggregate(
        finished=Count("id", filter=Q(status=TournamentStatus.FINISHED), distinct=True),
        ongoing=Count("id", filter=Q(status=TournamentStatus.ACTIVE), distinct=True),
        scheduled=Count("id", filter=Q(status=TournamentStatus.DRAFT), distinct=True),
    )

    matches_summary = get_matches_table(
        season_id=season_id, admin_id=admin_id
    ).aggregate(
        finished=Count("id", filter=Q(status=Match.Status.FINISHED), distinct=True),
        ongoing=Count("id", filter=Q(status=Match.Status.IN_PROGRESS), distinct=True),
        scheduled=Count("id", filter=Q(status=Match.Status.SCHEDULED), distinct=True),
    )

    members_summary = {
        "athletes": get_athletes_table(admin_id=admin_id).count(),
        "staff": get_staff_table().count(),
    }

    return SeasonSummaryDTO(
        id=season.id,
        name=season.name,
        modality_types_count=modality_types_qs.distinct().count(),
        active_modalities_count=active_modalities_qs.distinct().count(),
        active_courses_count=active_courses_qs.distinct().count(),
        teams_count=teams_qs.distinct().count(),
        tournaments_summary=tournaments_summary,
        matches_summary=matches_summary,
        members_summary=members_summary,
    )
