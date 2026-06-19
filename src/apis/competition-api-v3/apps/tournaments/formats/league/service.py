import uuid
from typing import Literal

from django.db.models import F
from infra.events.utils import emit_schema_event
from taca_events.pydantic_schemas.tournaments import (
    TournamentLeagueStandingsUpdatedData,
    TournamentLeagueStandingsUpdatedV1,
)

from ..base import BaseFormat, Match
from .models import DrawRule, LeagueSettings, LeagueStanding


class LeagueFormat(BaseFormat):

    # helper methods
    def _emit_standings_updated_event(self):
        # emit event to OutboxTable
        standings = self.get_details()["standings"]

        emit_schema_event(
            event=TournamentLeagueStandingsUpdatedV1(
                data=TournamentLeagueStandingsUpdatedData(
                    tournament_id=self.tournament.id,
                    standings=[
                        TournamentLeagueStandingsUpdatedData.Entry(
                            competitor_id=s["competitor_id"],
                            points=s["format_meta"]["points"],
                            played=s["format_meta"]["played"],
                            wins=s["format_meta"]["wins"],
                            draws=s["format_meta"]["draws"],
                            losses=s["format_meta"]["losses"],
                            points_for=s["format_meta"]["points_for"],
                            points_against=s["format_meta"]["points_against"],
                            position=s["position"],
                        )
                        for s in standings
                    ],
                )
            ),
            aggregate_id=self.tournament.id,
        )

    def _recalculate_standings_league_points(self):
        """Recalculate points for all standings based on current league settings. This should be called after any change in league settings to ensure standings are up to date."""
        standings = LeagueStanding.objects.filter(
            competitor__tournament=self.tournament
        ).all()
        for standing in standings:
            standing.points = (
                standing.wins * self.tournament.league_settings.win_points
                + standing.draws * self.tournament.league_settings.draw_points
                + standing.losses * self.tournament.league_settings.loss_points
            )
            standing.save()

        self._emit_standings_updated_event()
        return

    def _calculate_match_result(
        self, match: Match
    ) -> dict[uuid.UUID, Literal["winner", "loser", "draw"]]:
        results = {}
        for participant in match.participants.all():
            competitor = participant.competitor
            if participant.score is None and participant.position is None:
                return None

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

    # public methods
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

        self._recalculate_standings_league_points()
        return self.get_details()

    def get_details(self) -> dict:
        settings = LeagueSettings.objects.get(tournament=self.tournament)
        if not settings:
            raise ValueError("League settings not found for this tournament.")

        # get current standings
        standings = LeagueStanding.objects.filter(
            competitor__tournament=self.tournament
        )

        # apply draw rule if specified
        if settings.draw_rule == DrawRule.POINTS_DIFFERENCE:
            standings = standings.annotate(
                points_difference=F("points_for") - F("points_against")
            ).order_by("-points", "-points_difference")
        elif settings.draw_rule == DrawRule.POINTS_SCORED:
            standings = standings.order_by("-points", "-points_for")
        else:
            standings = standings.order_by("-points")

        # Calculate position
        standing_list = []
        current_position = 1
        last_points = None
        last_scored_conceded_diff = None
        last_scored = None
        for i, s in enumerate(standings.all(), start=1):
            if last_points is not None and (s.points < last_points):
                current_position = (
                    i  # update position if points are lower than previous competitor
                )
            elif last_points is not None and s.points == last_points:

                # If points are the same, check tiebreaker policy
                if settings.draw_rule == DrawRule.POINTS_DIFFERENCE:
                    scored_conceded_diff = s.points_for - s.points_against
                    if (
                        last_scored_conceded_diff is not None
                        and scored_conceded_diff < last_scored_conceded_diff
                    ):
                        current_position = i  # update position if points difference is lower than previous competitor

                elif settings.draw_rule == DrawRule.POINTS_SCORED:
                    if last_scored is not None and s.points_for < last_scored:
                        current_position = i  # update position if scored points is lower than previous competitor
                else:
                    pass  # no tiebreaker, competitors with same points share the same position

            last_points = s.points
            last_scored_conceded_diff = s.points_for - s.points_against
            last_scored = s.points_for

            standing_list.append(
                {
                    "competitor_id": s.competitor.id,
                    "position": current_position,
                    "format_meta": {
                        "played": s.played,
                        "points": s.points,
                        "wins": s.wins,
                        "draws": s.draws,
                        "losses": s.losses,
                        "points_for": s.points_for,
                        "points_against": s.points_against,
                        "differential": s.points_for - s.points_against,
                    },
                }
            )

        return {
            "settings": {
                "win_points": settings.win_points,
                "draw_points": settings.draw_points,
                "loss_points": settings.loss_points,
                "draw_rule": settings.draw_rule,
            },
            "standings": standing_list,
        }

    def record_result(self, match: Match) -> dict:

        results_map = self._calculate_match_result(match)

        if results_map is None:
            return self.get_details()

        total_points_for_match = sum(
            participant.score
            for participant in match.participants.all()
            if participant.score is not None
        )
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
            standing.points_for += (
                participant.score if participant.score is not None else 0
            )
            standing.points_against += (
                total_points_for_match - participant.score
                if participant.score is not None
                else 0
            )
            standing.save()

        self._emit_standings_updated_event()
        return self.get_details()

    def delete_result(self, match: Match) -> dict:
        results_map = self._calculate_match_result(match)

        if results_map is None:
            return self.get_details()

        total_points_for_match = sum(
            participant.score
            for participant in match.participants.all()
            if participant.score is not None
        )
        for participant in match.participants.all():
            competitor = participant.competitor
            result = results_map.get(competitor.id)
            if result is None:
                raise ValueError(
                    f"No result calculated for competitor {competitor.id} in match {match.id}"
                )

            standing = LeagueStanding.objects.get(competitor=competitor)

            if result == "winner":
                standing.points -= self.tournament.league_settings.win_points
                standing.wins -= 1
            elif result == "loser":
                standing.points -= self.tournament.league_settings.loss_points
                standing.losses -= 1
            elif result == "draw":
                standing.points -= self.tournament.league_settings.draw_points
                standing.draws -= 1

            standing.played -= 1
            standing.points_for -= (
                participant.score if participant.score is not None else 0
            )
            standing.points_against -= (
                total_points_for_match - participant.score
                if participant.score is not None
                else 0
            )
            standing.save()

        self._emit_standings_updated_event()
        return self.get_details()
