"""
Tournaments management service
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from admin_api.clients.modalities_service import (
    ModalityDTO,
    StudentDTO,
    TeamDTO,
    modalities_service_client,
)
from admin_api.clients.ranking_service import ranking_service_client
from admin_api.clients.tournaments_service import (
    TournamentDTO,
    tournaments_service_client,
)


@dataclass
class Modality:
    id: str
    name: str


@dataclass
class ScoringFormat:
    name: str
    rank: str
    points: List[int]


@dataclass
class Competitor:
    id: str
    name: str
    course_name: str
    entity_id: str


@dataclass
class _Season:
    id: int
    name: str


@dataclass
class _StandingsEntry:
    competitor_id: str
    # competitor_name: str
    # competitor_course_name: str
    position: int
    points: Optional[int] = None


@dataclass
class Tournament:
    id: str
    name: str
    status: str
    modality: Modality
    start_date: str
    competitor_type: str

    competitors: List[Competitor] = field(default_factory=list)
    scoring_format: ScoringFormat = None
    season: _Season = None
    standings: List[_StandingsEntry] = None


class TeamDoesNotBelongToSeasonError(ValueError):
    pass


class TournamentsService:
    """Service for tournament management"""

    # Helper methods to build domain objects from DTOs and to populate additional data by calling other services
    def _populate_tournament_scoring_format(
        self,
        tournament: Tournament,
        tournament_dto: TournamentDTO,
        force_playoff_scoring_format: bool,
    ) -> None:
        """
        Populate the scoring format information for a tournament based on its modality and the number of competitors, by fetching the necessary data from the modalities and ranking services.

        Args:
            tournament (Tournament): The tournament domain object to populate the scoring format for. This object will be modified in place.
            tournament_dto (TournamentDTO): The tournament data transfer object received from the tournaments service, which contains the raw data needed to determine the scoring format.
            force_playoff_scoring_format (bool): Whether to force the use of playoff scoring format. Needed for cases when events may not have processed the update yet.

        Returns:
            None: This method modifies the provided tournament object in place and does not return anything.
        """

        scoring_format_type = None
        if force_playoff_scoring_format:
            scoring_format_type = (
                modalities_service_client.modality_types.get_playoff_modality_type()
            )
        else:
            scoring_format_type = (
                modalities_service_client.modality_types.get_modality_type(
                    tournament_dto.scoring_format_id
                )
            )

        scoring_format = ranking_service_client.calculate_tournament_tier(
            tournament_id=tournament.id,
            modality_type_id=scoring_format_type.id,
            participant_count=len(tournament_dto.competitors),
        )
        tournament.scoring_format = ScoringFormat(
            name=scoring_format_type.name,
            rank=scoring_format.rank,
            points=scoring_format.points,
        )

    def _populate_tournament_competitors(
        self, tournament: Tournament, tournament_dto: TournamentDTO
    ) -> None:
        """
        Populate the competitors information for a tournament based on the competitors data in the tournament DTO, by fetching the necessary data from the modalities service.

        Args:
            tournament (Tournament): The tournament domain object to populate the competitors for. This object will be modified in place.
            tournament_dto (TournamentDTO): The tournament data transfer object received from the tournaments service, which contains the raw competitors data.

        Returns:
            None: This method modifies the provided tournament object in place and does not return anything.
        """
        athlete_ids = [
            c.competitor_entity_id
            for c in tournament_dto.competitors
            if c.competitor_type == "athlete"
        ]
        team_ids = [
            c.competitor_entity_id
            for c in tournament_dto.competitors
            if c.competitor_type == "team"
        ]

        athletes = (
            modalities_service_client.students.get_students_by_ids(athlete_ids)
            if athlete_ids
            else {}
        )
        teams = (
            modalities_service_client.teams.get_teams_by_ids(team_ids)
            if team_ids
            else {}
        )

        for competitor_dto in tournament_dto.competitors:
            course_name = None
            competitor_name = None

            if competitor_dto.competitor_type == "athlete":
                athlete = athletes.get(competitor_dto.competitor_entity_id)
                if athlete:
                    course_name = athlete.course.name
                    competitor_name = athlete.full_name
            elif competitor_dto.competitor_type == "team":
                team = teams.get(competitor_dto.competitor_entity_id)
                if team:
                    course_name = team.course.name
                    competitor_name = team.name

            tournament.competitors.append(
                Competitor(
                    id=competitor_dto.id,
                    name=competitor_name,
                    course_name=course_name,
                    entity_id=competitor_dto.competitor_entity_id,
                )
            )

    def _populate_tournament_season(
        self, tournament: Tournament, tournament_dto: TournamentDTO
    ) -> None:
        """
        Populate the season information for a tournament based on the season data in the tournament DTO, by fetching the necessary data from the modalities service.

        Args:
            tournament (Tournament): The tournament domain object to populate the season for. This object will be modified in place.
            tournament_dto (TournamentDTO): The tournament data transfer object received from the tournaments service, which contains the raw season data.

        Returns:
            None: This method modifies the provided tournament object in place and does not return anything.
        """
        season_data = modalities_service_client.seasons.get_season(
            tournament_dto.season_id
        )
        tournament.season = _Season(id=season_data.id, name=season_data.name)

    def _build_tournament_from_dto(
        self,
        tournament_dto: TournamentDTO,
        *,
        modalities_data: dict[str, ModalityDTO] = None,
        include_details: bool = False,
        force_playoff_scoring_format: bool = False,
    ) -> Tournament:
        """Helper method to build a Tournament domain object from a TournamentDTO, fetching the modality data as needed

        Args:
            tournament_dto (TournamentDTO): The tournament data transfer object received from the tournaments service
            modalities_data (dict[str, ModalityDTO]): A dictionary of modality data that can be used to avoid fetching modality data multiple times (to prevent N+1 problem). The keys are modality IDs and the values are ModalityDTO objects.
            include_details (bool): Whether to include detailed information in the constructed Tournament object.
            force_playoff_scoring_format (bool): Whether to force the use of playoff scoring format. Needed for cases when events may not have processed the update yet.

        Raises:
            ValueError: If the modality data cannot be found for the given tournament DTO

        Returns:
            Tournament: The constructed Tournament domain object
        """
        if modalities_data is None:
            modalities_data = {}

        # First try to get the modality from the provided data, if not found, fetch it from the modalities service
        modality = None
        if tournament_dto.modality_id in modalities_data:
            modality = modalities_data.get(tournament_dto.modality_id)
        else:
            modality = modalities_service_client.modalities.get_modality(
                tournament_dto.modality_id
            )

        # If modality is still not found, raise an error (this should not happen, but it's better to fail fast than to return incomplete data)
        if not modality:
            raise ValueError(f"Modality not found for ID: {tournament_dto.modality_id}")

        # Build the Tournament domain object
        tournament = Tournament(
            id=tournament_dto.id,
            name=tournament_dto.name,
            status=tournament_dto.status,
            modality=modality,
            start_date=tournament_dto.start_date,
            competitor_type=tournament_dto.competitor_type,
        )

        if include_details:
            # Add scoring format of the tournament based on its modality and the number of competitors
            self._populate_tournament_scoring_format(
                tournament, tournament_dto, force_playoff_scoring_format
            )

            # Add competitors information to the tournament
            self._populate_tournament_competitors(tournament, tournament_dto)

            # Add season information to the tournament
            self._populate_tournament_season(tournament, tournament_dto)

            # Add standings information to the tournament if it's finished
            if tournament.status == "finished":
                print("Populating tournament standings...", flush=True)
                tournament.standings = []
                for entry in tournament_dto.ranking_positions:
                    tournament.standings.append(
                        _StandingsEntry(
                            competitor_id=entry.competitor_id,
                            position=entry.position,
                        )
                    )

        return tournament

    # Public methods for tournament management, which will be called by the API views/controllers
    def list_tournaments(
        self, status: str = None, modality_id: str = None, season_id: int = None
    ) -> list[Tournament]:
        """List all tournaments"""

        # If season_id is not provided, get the current season id from the modalities service
        if season_id is None:
            season_id = modalities_service_client.seasons.get_current_season().id

        tournaments_raw_data = tournaments_service_client.list_tournaments(
            status_filter=status, modality_id=modality_id, season_id=season_id
        )

        # Fetch all relevant modalities in a single call to avoid N+1 problem
        relevant_modalities_ids = list(set(t.modality_id for t in tournaments_raw_data))
        modalities_data = modalities_service_client.modalities.get_modalities_by_ids(
            relevant_modalities_ids
        )

        return [
            self._build_tournament_from_dto(
                tournament_dto, modalities_data=modalities_data
            )
            for tournament_dto in tournaments_raw_data
        ]

    def create_tournament(
        self,
        name: str,
        modality_id: str,
        is_playoff: bool = False,
        season_id: int = None,
    ) -> Tournament:
        """Create a new tournament"""

        # fetch the modality to ensure it exists and to get the necessary data for tournament creation
        modality = modalities_service_client.modalities.get_modality(modality_id)

        # infer the scoring format based on whether it's a playoff or not.
        scoring_format_id = None
        if is_playoff:
            playoff_modality_type = (
                modalities_service_client.modality_types.get_playoff_modality_type()
            )
            if not playoff_modality_type:
                raise ValueError(
                    "No playoff modality type found, cannot create playoff tournament"
                )
            scoring_format_id = playoff_modality_type.id
        else:
            scoring_format_id = modality.modality_type.id

        # get current season id if not provided
        if season_id is None:
            season_id = modalities_service_client.seasons.get_current_season().id

        tournament_dto = tournaments_service_client.create_tournament(
            modality_id=modality_id,
            name=name,
            scoring_format_id=scoring_format_id,
            competitor_type=modality.modality_type.tournament_competitor_type.replace(
                "individual", "athlete"
            ),  # the tournaments service expects "athlete" instead of "individual"
            start_date=datetime.now().isoformat(),
            season_id=season_id,
        )

        return self._build_tournament_from_dto(
            tournament_dto,
            modalities_data={
                modality.id: modality
            },  # since we already have the modality data, we can pass it directly
        )

    def get_tournament(self, tournament_id: str) -> Tournament:
        """Get tournament details"""

        tournament_dto = tournaments_service_client.get_tournament(tournament_id)

        return self._build_tournament_from_dto(
            tournament_dto,
            include_details=True,
        )

    def update_tournament(
        self,
        tournament_id: str,
        name: str = None,
        start_date: str = None,
        status: str = None,
        is_playoff: bool = None,
    ) -> Tournament:
        """Update tournament details"""

        # get tournament modality
        tournament_modality = modalities_service_client.modalities.get_modality(
            tournaments_service_client.get_tournament(tournament_id).modality_id
        )

        # If the tournament is being updated to be a playoff, we need to fetch the playoff modality type to get its ID for the update request
        scoring_format_id = None
        if is_playoff is not None:
            scoring_format_id = (
                tournament_modality.modality_type.id
            )  # default to the current modality type's scoring format if changing not playoff status

            if is_playoff:
                # If changing to playoff, we need to get the playoff modality type
                playoff_modality_type = (
                    modalities_service_client.modality_types.get_playoff_modality_type()
                )
                if not playoff_modality_type:
                    raise ValueError(
                        "No playoff modality type found, cannot update tournament to be a playoff"
                    )
                scoring_format_id = playoff_modality_type.id

        tournament_dto = tournaments_service_client.update_tournament(
            tournament_id=tournament_id,
            name=name,
            start_date=start_date,
            status=status,
            scoring_format_id=scoring_format_id,
        )

        return self._build_tournament_from_dto(
            tournament_dto,
            modalities_data={tournament_modality.id: tournament_modality},
            include_details=True,
            # if is_playoff is None, it means playoff status is not being changed, so we should not force playoff scoring format
            force_playoff_scoring_format=(
                is_playoff if is_playoff is not None else False
            ),
        )

    def delete_tournament(self, tournament_id: str) -> None:
        """Delete a tournament"""
        tournaments_service_client.delete_tournament(tournament_id)

    def finish_tournament(
        self, tournament_id: str, ranking_entries: List[dict]
    ) -> Tournament:
        """Finish a tournament by providing the final ranking entries"""

        tournament_dto = tournaments_service_client.finish_tournament(
            tournament_id=tournament_id,
            ranking_entries=ranking_entries,
            finished_by="00000000-0000-0000-0000-000000000000",
        )

        return self._build_tournament_from_dto(
            tournament_dto,
            include_details=True,
        )

    def add_competitors(
        self, tournament_id: str, competitors_data: List[dict]
    ) -> Tournament:
        """Add competitors to a tournament"""

        # gather necessary data for competitors addition
        athletes = []
        teams = []
        for competitor in competitors_data:
            entity_id = competitor["entity_id"]
            competitor_type = competitor["competitor_type"]
            if competitor_type == "athlete":
                athletes.append(entity_id)
            elif competitor_type == "team":
                teams.append(entity_id)

        mapper: Dict[str, List[StudentDTO | TeamDTO]] = {
            "athlete": (
                modalities_service_client.students.get_students_by_ids(athletes)
                if athletes
                else {}
            ),
            "team": (
                modalities_service_client.teams.get_teams_by_ids(teams) if teams else {}
            ),
        }

        # prepare the competitor data in the format expected by the tournaments service
        processed_competitors_data = []
        for competitor in competitors_data:
            if (
                competitor["competitor_type"] == "athlete"
                and competitor["entity_id"] not in mapper["athlete"]
            ):
                raise ValueError(f"Athlete with ID {competitor['entity_id']} not found")
            if (
                competitor["competitor_type"] == "team"
                and competitor["entity_id"] not in mapper["team"]
            ):
                raise ValueError(f"Team with ID {competitor['entity_id']} not found")

            processed_competitors_data.append(
                {
                    "competitor_type": competitor["competitor_type"],
                    "competitor_entity_id": str(competitor["entity_id"]),
                    "competitor_course_id": mapper[competitor["competitor_type"]][
                        competitor["entity_id"]
                    ].course.id,
                }
            )

        # teams need to belong to the same season as the tournament
        if teams:
            tournament_season_id = tournaments_service_client.get_tournament(
                tournament_id
            ).season_id
            for team_id in teams:
                team: TeamDTO = mapper["team"][team_id]
                if team.season.id != tournament_season_id:
                    raise TeamDoesNotBelongToSeasonError(
                        f"Team with ID {team_id} belongs to season {team.season.id}, but tournament belongs to season {tournament_season_id}"
                    )

        tournament_dto = tournaments_service_client.add_competitors(
            tournament_id=tournament_id, competitors_data=processed_competitors_data
        )

        return self._build_tournament_from_dto(
            tournament_dto,
            include_details=True,
        )

    def remove_competitors(
        self, tournament_id: str, competitor_ids: List[str]
    ) -> Tournament:
        """Remove competitors from a tournament"""

        tournament_dto = tournaments_service_client.remove_competitors(
            tournament_id=tournament_id, competitors_ids=competitor_ids
        )

        return self._build_tournament_from_dto(
            tournament_dto,
            include_details=True,
        )


tournaments_service = TournamentsService()
