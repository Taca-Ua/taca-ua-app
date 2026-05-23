"""
Seasons management service
"""

from dataclasses import dataclass

from admin_api.clients.matches_service import matches_service_client
from admin_api.clients.modalities_service import SeasonDTO, modalities_service_client
from admin_api.clients.tournaments_service import tournaments_service_client


@dataclass
class Season:
    id: int
    name: str


@dataclass
class SeasonSummary:
    @dataclass
    class _TournamentSummary:
        finished: int
        ongoing: int
        scheduled: int

    @dataclass
    class _MatchesSummary:
        finished: int
        ongoing: int
        scheduled: int

    @dataclass
    class _MembersSummary:
        athletes: int
        staff: int

    id: int
    name: str

    modality_types_count: int
    active_modalities_count: int
    active_courses_count: int
    teams_count: int
    tournaments_summary: _TournamentSummary
    matches_summary: _MatchesSummary
    members_summary: _MembersSummary


class SeasonService:

    def _build_season_from_dto(self, dto: SeasonDTO) -> Season:
        return Season(id=dto.id, name=dto.name)

    def list_seasons(self) -> list[Season]:
        season_dtos = modalities_service_client.seasons.list_seasons()
        return [self._build_season_from_dto(dto) for dto in season_dtos]

    def create_season(self, name: str, admin_id: str) -> Season:
        new_season_dto = modalities_service_client.seasons.create_season(
            name=name, created_by=admin_id
        )
        return self._build_season_from_dto(new_season_dto)

    def get_current_season(self) -> Season | None:
        current_season_dto = modalities_service_client.seasons.get_current_season()
        if not current_season_dto:
            return None
        return self._build_season_from_dto(current_season_dto)

    def get_season_summary(
        self, season_id: int = None, admin_id: str = None
    ) -> SeasonSummary | None:
        """Get summary information for a specific season.

        Args:
            season_id (int, optional): The ID of the season for which to retrieve summary information. Defaults to None.
            admin_id (str, optional): The ID of the administrator. Defaults to None.

        Returns:
            SeasonSummary | None: The summary information for the specified season, or None if not found.
        """

        if season_id is None:
            current_season_dto = modalities_service_client.seasons.get_current_season()
            if not current_season_dto:
                return None
            season_id = current_season_dto.id

        modalities_summary_dto = modalities_service_client.seasons.get_season_summary(
            season_id, admin_id=admin_id
        )
        tournaments_summary = tournaments_service_client.get_tournaments_summary(
            season_id,
            teams_ids=modalities_summary_dto.admin_teams_ids,
            athletes_ids=modalities_summary_dto.admin_athletes_ids,
        )
        matches_summary = matches_service_client.get_matches_summary(
            tournaments_ids=tournaments_summary.tournaments_ids,
            tournaments_distribution=(
                {
                    str(tc.tournament_id): [str(a_id) for a_id in tc.competitors_ids]
                    for tc in tournaments_summary.competitors_distribution
                }
                if tournaments_summary.competitors_distribution
                else None
            ),
        )

        return SeasonSummary(
            id=modalities_summary_dto.id,
            name=modalities_summary_dto.name,
            modality_types_count=modalities_summary_dto.modality_types_count,
            active_modalities_count=modalities_summary_dto.active_modalities_count,
            active_courses_count=modalities_summary_dto.active_courses_count,
            teams_count=modalities_summary_dto.teams_count,
            members_summary=SeasonSummary._MembersSummary(
                athletes=modalities_summary_dto.athletes_count,
                staff=modalities_summary_dto.staff_count,
            ),
            tournaments_summary=SeasonSummary._TournamentSummary(
                finished=tournaments_summary.tournaments_finished,
                ongoing=tournaments_summary.tournaments_ongoing,
                scheduled=tournaments_summary.tournaments_scheduled,
            ),
            matches_summary=SeasonSummary._MatchesSummary(
                finished=matches_summary.finished,
                ongoing=matches_summary.ongoing,
                scheduled=matches_summary.scheduled,
            ),
        )


seasons_service = SeasonService()
