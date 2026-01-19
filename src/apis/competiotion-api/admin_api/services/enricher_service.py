from typing import List

from .matches_service import matches_service_client
from .modalities_service import modalities_service_client


class EnricherService:
    """Service responsible for enriching data combining information from multiple services."""

    def __init__(self):
        pass

    def complete_tournament_info(self, tournament: dict) -> dict:
        """Enrich tournament data with modality, teams, and detailed matches information.
        The changes are made in place to the input tournament dictionary.

        Args:
                tournament (dict): Tournament data to be enriched.

        Returns:
                dict: Enriched tournament data.
        """

        # Enrich matches with complete match details
        tournament["modality"] = modalities_service_client.get_modality(
            tournament["modality_id"]
        )

        # Fetch and enrich teams data
        team_ids = []
        for competitor in tournament.get("competitors", []):
            if competitor["competitor_type"] == "team":
                team_ids.append(competitor["competitor"]["team_id"])
        teams_data = modalities_service_client.get_teams_by_ids(team_ids)
        teams_data_map = {team["id"]: team for team in teams_data}
        for competitor in tournament.get("competitors", []):
            if competitor["competitor_type"] == "team":
                competitor["team"] = teams_data_map.get(
                    competitor["competitor"]["team_id"]
                )

        # Fetch and enrich matches data
        tournament_matches = matches_service_client.list_matches(
            tournament_id=tournament["id"]
        ).get("matches", [])

        self.complete_matches_info(tournament_matches)
        tournament["matches"] = tournament_matches

        return tournament

    def complete_matches_info(self, matches: List[dict]) -> List[dict]:
        """Enrich a list of matches with detailed participant information.
        The changes are made in place to the input matches list.

        Args:
                matches (List[dict]): List of match data to be enriched.

        Returns:
                List[dict]: List of enriched match data.
        """

        athlete_ids_to_fetch = {}
        teams_ids_to_fetch = {}

        # Collect all athlete and team IDs to fetch
        for match in matches:
            for participant in match["participants"]:
                # Collect team IDs
                if participant.get("team_id", None):
                    if participant["team_id"] not in teams_ids_to_fetch:
                        teams_ids_to_fetch[participant["team_id"]] = []

                    teams_ids_to_fetch[participant["team_id"]].append(participant)

                # Collect athlete IDs
                if participant.get("athlete_id", None):
                    if participant["athlete_id"] not in athlete_ids_to_fetch:
                        athlete_ids_to_fetch[participant["athlete_id"]] = []

                    athlete_ids_to_fetch[participant["athlete_id"]].append(participant)

        # Fetch all athletes data in a single call
        if athlete_ids_to_fetch:
            students_data = modalities_service_client.get_students_by_ids(
                list(athlete_ids_to_fetch.keys())
            )
            students_data_map = {student["id"]: student for student in students_data}

            for athlete_id, participants in athlete_ids_to_fetch.items():
                for participant in participants:
                    participant["athlete"] = students_data_map.get(athlete_id)

        # Fetch all teams data in a single call
        if teams_ids_to_fetch:
            teams_data = modalities_service_client.get_teams_by_ids(
                list(teams_ids_to_fetch.keys())
            )
            teams_data_map = {team["id"]: team for team in teams_data}

            for team_id, participants in teams_ids_to_fetch.items():
                for participant in participants:
                    participant["team"] = teams_data_map.get(team_id)

        return matches


enricher_service = EnricherService()
