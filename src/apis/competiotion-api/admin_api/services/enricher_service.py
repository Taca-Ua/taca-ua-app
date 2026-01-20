from typing import List

from .matches_service import MatchDTO, matches_service_client
from .modalities_service import modalities_service_client
from .tournaments_service import TournamentDTO


class EnricherService:
    """Service responsible for enriching data combining information from multiple services."""

    def __init__(self):
        pass

    def complete_tournament_info(self, tournament: TournamentDTO) -> TournamentDTO:
        """Enrich tournament data with modality, teams, and detailed matches information.
        The changes are made in place to the input tournament dictionary.

        Args:
                tournament (TournamentDTO): Tournament data to be enriched.

        Returns:
                TournamentDTO: Enriched tournament data.
        """

        # Enrich matches with complete match details
        tournament.modality = modalities_service_client.get_modality(
            tournament.modality_id
        )

        # Fetch and enrich teams data
        team_ids = []
        for competitor in tournament.competitors:
            if competitor.competitor_type == "team":
                team_ids.append(competitor.competitor["team_id"])

        teams_data = modalities_service_client.get_teams_by_ids(team_ids)
        teams_data_map = {team.id: team for team in teams_data}

        for competitor in tournament.competitors:
            if competitor.competitor_type == "team":
                competitor.team = teams_data_map.get(competitor.competitor["team_id"])

        # Fetch and enrich matches data
        tournament_matches = matches_service_client.list_matches(
            tournament_id=tournament.id
        )

        self.complete_matches_info(tournament_matches)
        tournament.matches = tournament_matches

        return tournament

    def complete_matches_info(self, matches: List[MatchDTO]) -> List[MatchDTO]:
        """Enrich a list of matches with detailed participant information.
        The changes are made in place to the input matches list.

        Args:
                matches (List[MatchDTO]): List of match data to be enriched.

        Returns:
                List[MatchDTO]: List of enriched match data.
        """

        athlete_ids_to_fetch = {}
        teams_ids_to_fetch = {}

        # Collect all athlete and team IDs to fetch
        for match in matches:
            for participant in match.participants:
                # Collect team IDs
                if participant.team_id:
                    if participant.team_id not in teams_ids_to_fetch:
                        teams_ids_to_fetch[participant.team_id] = []

                    teams_ids_to_fetch[participant.team_id].append(participant)

                # Collect athlete IDs
                if participant.athlete_id:
                    if participant.athlete_id not in athlete_ids_to_fetch:
                        athlete_ids_to_fetch[participant.athlete_id] = []

                    athlete_ids_to_fetch[participant.athlete_id].append(participant)

        # Fetch all athletes data in a single call
        if athlete_ids_to_fetch:
            students_data = modalities_service_client.get_students_by_ids(
                list(athlete_ids_to_fetch.keys())
            )
            students_data_map = {student.id: student for student in students_data}

            for athlete_id, participants in athlete_ids_to_fetch.items():
                for participant in participants:
                    participant.athlete = students_data_map.get(athlete_id)

        # Fetch all teams data in a single call
        if teams_ids_to_fetch:
            teams_data = modalities_service_client.get_teams_by_ids(
                list(teams_ids_to_fetch.keys())
            )
            teams_data_map = {team.id: team for team in teams_data}

            for team_id, participants in teams_ids_to_fetch.items():
                for participant in participants:
                    participant.team = teams_data_map.get(team_id)

        return matches

    def complete_participant_info(self, participants: List) -> List:
        """Enrich a list of participants with detailed team/athlete information.
        The changes are made in place to the input participants list.

        Args:
            participants (List): List of participant data to be enriched.

        Returns:
            List: List of enriched participant data.
        """
        athlete_ids_to_fetch = {}
        teams_ids_to_fetch = {}

        # Collect all athlete and team IDs to fetch
        for participant in participants:
            # Collect team IDs
            if hasattr(participant, "team_id") and participant.team_id:
                if participant.team_id not in teams_ids_to_fetch:
                    teams_ids_to_fetch[participant.team_id] = []
                teams_ids_to_fetch[participant.team_id].append(participant)

            # Collect athlete IDs
            if hasattr(participant, "athlete_id") and participant.athlete_id:
                if participant.athlete_id not in athlete_ids_to_fetch:
                    athlete_ids_to_fetch[participant.athlete_id] = []
                athlete_ids_to_fetch[participant.athlete_id].append(participant)

        # Fetch all athletes data in a single call
        if athlete_ids_to_fetch:
            students_data = modalities_service_client.get_students_by_ids(
                list(athlete_ids_to_fetch.keys())
            )
            students_data_map = {student.id: student for student in students_data}

            for athlete_id, participants_list in athlete_ids_to_fetch.items():
                for participant in participants_list:
                    participant.athlete = students_data_map.get(athlete_id)

        # Fetch all teams data in a single call
        if teams_ids_to_fetch:
            teams_data = modalities_service_client.get_teams_by_ids(
                list(teams_ids_to_fetch.keys())
            )
            teams_data_map = {team.id: team for team in teams_data}

            for team_id, participants_list in teams_ids_to_fetch.items():
                for participant in participants_list:
                    participant.team = teams_data_map.get(team_id)

        return participants

    def complete_lineup_info(self, lineup_entries: List) -> List:
        """Enrich a list of lineup entries with detailed player information.
        The changes are made in place to the input lineup list.

        Args:
            lineup_entries (List): List of lineup entries to be enriched.

        Returns:
            List: List of enriched lineup entries.
        """
        player_ids_to_fetch = {}

        # Collect all player IDs to fetch
        for entry in lineup_entries:
            if hasattr(entry, "player_id") and entry.player_id:
                if entry.player_id not in player_ids_to_fetch:
                    player_ids_to_fetch[entry.player_id] = []
                player_ids_to_fetch[entry.player_id].append(entry)

        # Fetch all players data in a single call
        if player_ids_to_fetch:
            students_data = modalities_service_client.get_students_by_ids(
                list(player_ids_to_fetch.keys())
            )
            students_data_map = {student.id: student for student in students_data}

            for player_id, entries_list in player_ids_to_fetch.items():
                for entry in entries_list:
                    entry.player = students_data_map.get(player_id)

        return lineup_entries


enricher_service = EnricherService()
