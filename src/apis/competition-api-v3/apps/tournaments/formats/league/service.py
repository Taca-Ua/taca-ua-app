import uuid
from typing import Literal

from ..base import BaseFormat, Match
from .models import DrawRule, LeagueSettings, LeagueStanding


class LeagueFormat(BaseFormat):

    def create(self, format_data: dict):
        LeagueSettings.objects.create(
            tournament=self.tournament,
            win_points=format_data.get("win_points", 3),
            draw_points=format_data.get("draw_points", 1),
            loss_points=format_data.get("loss_points", 0),
            draw_rule=format_data.get("draw_rule"),
        )

        return self.get_details()

    def update(self, format_data: dict):
        settings = LeagueSettings.objects.get(tournament=self.tournament)
        if not settings:
            raise ValueError("League settings not found for this tournament.")

        print(f"Updating league format with data: {format_data}")

        settings.win_points = format_data.get("win_points", settings.win_points)
        settings.draw_points = format_data.get("draw_points", settings.draw_points)
        settings.loss_points = format_data.get("loss_points", settings.loss_points)

        if (
            "draw_rule" in format_data
            and (format_data["draw_rule"] in DrawRule.values)
            or format_data["draw_rule"] is None
        ):
            settings.draw_rule = format_data.get("draw_rule", settings.draw_rule)
        else:
            raise ValueError(
                f"Invalid draw rule: {format_data['draw_rule']}. Must be one of {DrawRule.values} or None."
            )

        settings.save()

        return self.get_details()

    def get_details(self) -> dict:
        settings = LeagueSettings.objects.get(tournament=self.tournament)
        if not settings:
            raise ValueError("League settings not found for this tournament.")

        return {
            "win_points": settings.win_points,
            "draw_points": settings.draw_points,
            "loss_points": settings.loss_points,
            "draw_rule": settings.draw_rule,
        }

    def _calculate_match_result(
        self, match: Match
    ) -> dict[uuid.UUID, Literal["winner", "loser", "draw"]]:
        results = {}
        for participant in match.participants.all():
            competitor = participant.competitor
            results[competitor.id] = {
                "score": participant.score,
                "position": participant.position,
            }

        participant_results_map: dict[uuid.UUID, Literal["winner", "loser", "draw"]] = (
            {}
        )
        if all(score is not None for score in [p["score"] for p in results.values()]):
            # score-based result calculation.
            # Most points wins, ties if all competitors have same points
            max_score = max(p["score"] for p in results.values())
            winners = [
                comp_id for comp_id, res in results.items() if res["score"] == max_score
            ]

            if len(winners) == 1:
                participant_results_map[winners[0]] = "winner"
                for comp_id in results.keys():
                    if comp_id != winners[0]:
                        participant_results_map[comp_id] = "loser"
            else:
                for comp_id in winners:
                    participant_results_map[comp_id] = "draw"
                for comp_id in results.keys():
                    if comp_id not in winners:
                        participant_results_map[comp_id] = "loser"

        elif all(
            position is not None
            for position in [p["position"] for p in results.values()]
        ):
            # position-based result calculation.
            # 1st place is winner, 2nd place is loser, ties if multiple competitors have same position
            min_position = min(p["position"] for p in results.values())
            winners = [
                comp_id
                for comp_id, res in results.items()
                if res["position"] == min_position
            ]

            if len(winners) == 1:
                participant_results_map[winners[0]] = "winner"
                for comp_id in results.keys():
                    if comp_id != winners[0]:
                        participant_results_map[comp_id] = "loser"
            else:
                for comp_id in winners:
                    participant_results_map[comp_id] = "draw"
                for comp_id in results.keys():
                    if comp_id not in winners:
                        participant_results_map[comp_id] = "loser"
        else:
            raise ValueError(
                "All participants must have either scores or positions to determine the match outcome."
            )

        return participant_results_map

    def record_result(self, match: Match) -> dict:

        results_map = self._calculate_match_result(match)

        for participant in match.participants.all():
            competitor = participant.competitor
            result = results_map.get(competitor.id)
            if result is None:
                raise ValueError(
                    f"No result calculated for competitor {competitor.id} in match {match.id}"
                )

            standing, created = LeagueStanding.objects.get_or_create(
                competitor=competitor,
                defaults={"points": 0, "played": 0, "wins": 0, "draws": 0, "losses": 0},
            )

            if result == "winner":
                standing.points += self.tournament.league_settings.win_points
                standing.wins += 1
            elif result == "loser":
                standing.points += self.tournament.league_settings.loss_points
                standing.losses += 1
            elif result == "draw":
                standing.points += self.tournament.league_settings.draw_points
                standing.draws += 1

            standing.played += 1
            standing.save()

        return self.get_details()
