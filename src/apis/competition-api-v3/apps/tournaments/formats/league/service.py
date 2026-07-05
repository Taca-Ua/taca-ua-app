import uuid
from dataclasses import dataclass
from typing import Dict, List, Literal

from apps.matches.models import Match
from apps.matches.service import create_match
from django.db.models import F
from rest_framework.exceptions import ValidationError

from ..base import BaseFormat, MatchSuggestion
from .models import DrawRule, LeagueMatch, LeagueSettings, LeagueStanding
from .utils import RoundRobinScheduler


@dataclass
class LeagueMatchGenerationConfiguration:
    """Configuration for generating matches in a league format."""

    players_per_match: int = (
        2  # Default to 2 players per match for a standard league format
    )
    number_of_faceoffs: int = 1  # Default to a single round-robin format

    def __post_init__(self):
        if isinstance(self.players_per_match, str) and self.players_per_match.isdigit():
            self.players_per_match = int(self.players_per_match)
        if (
            isinstance(self.number_of_faceoffs, str)
            and self.number_of_faceoffs.isdigit()
        ):
            self.number_of_faceoffs = int(self.number_of_faceoffs)

        if self.players_per_match < 2:
            raise ValidationError("Players per match must be at least 2.")
        if self.number_of_faceoffs < 1:
            raise ValidationError("Number of faceoffs must be at least 1.")


@dataclass
class LeagueSuggestedMatch(MatchSuggestion):
    format_specific_data: dict = None

    @property
    def round_number(self) -> int:
        if self.format_specific_data and "round_number" in self.format_specific_data:
            return self.format_specific_data["round_number"]
        return 1  # Default to round 1 if not specified

    def __post_init__(self):
        if len(self.competitors_ids) < 2:
            raise ValidationError("At least two competitors are required for a match.")

        if len(set(self.competitors_ids)) != len(self.competitors_ids):
            raise ValidationError(
                "Must be distinct competitors in a match. Duplicate competitor IDs found."
            )

        if "round_number" not in self.format_specific_data:
            raise ValidationError(
                "Round number must be specified in format_specific_data."
            )


class LeagueFormat(BaseFormat):

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
            raise ValidationError(
                "All participants must have either scores or positions to determine the match outcome."
            )

        return participant_results_map

    def _check_matches_configuration(
        self, matches_configuration: list[MatchSuggestion]
    ):
        # check that a competitor does not appear in more than one match in the same round
        round_competitor_map: Dict[int, set[uuid.UUID]] = {}
        for match_data in matches_configuration:
            round_number = match_data.format_specific_data.get("round_number", 1)
            if round_number not in round_competitor_map:
                round_competitor_map[round_number] = set()

            for competitor_id in match_data.competitors_ids:
                if competitor_id in round_competitor_map[round_number]:
                    raise ValidationError(
                        f"Competitor {competitor_id} appears in more than one match in round {round_number}."
                    )
                round_competitor_map[round_number].add(competitor_id)

        # check that all matchups have the same number of faceoffs
        matchups: Dict[tuple[uuid.UUID, ...], int] = {}
        for match_data in matches_configuration:
            matchup_key = tuple(sorted(match_data.competitors_ids))
            if matchup_key not in matchups:
                matchups[matchup_key] = 0
            matchups[matchup_key] += 1

        if len(set(matchups.values())) > 1:
            raise ValidationError(
                "All matchups must have the same number of faceoffs. Found varying counts."
            )

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
            raise ValidationError("League settings not found for this tournament.")

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
            raise ValidationError(
                f"Invalid draw rule: {format_data['draw_rule']}. Must be one of {DrawRule.values} or None."
            )

        settings.save()

        self._recalculate_standings_league_points()
        return self.get_details()

    def get_details(self) -> dict:
        settings = LeagueSettings.objects.get(tournament=self.tournament)
        if not settings:
            raise ValidationError("League settings not found for this tournament.")

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
                raise ValidationError(
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
                raise ValidationError(
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

        return self.get_details()

    def suggest_matches(self, configuration: dict) -> List[LeagueSuggestedMatch]:
        config = LeagueMatchGenerationConfiguration(**configuration)

        scheduler = RoundRobinScheduler(
            participants=list(self.tournament.competitors.values_list("id", flat=True)),
            match_size=config.players_per_match,
            num_faceoffs=config.number_of_faceoffs,
        )
        rounds = scheduler.generate(show_bye_matches=False)

        sugestion: List[LeagueSuggestedMatch] = []
        for idx, r in enumerate(rounds):
            for match in r:
                sugestion.append(
                    LeagueSuggestedMatch(
                        competitors_ids=list(match),
                        format_specific_data={"round_number": idx + 1},
                    )
                )

        # Check the generated matches configuration for validity (should go off, but just in case)
        self._check_matches_configuration(sugestion)
        return sugestion

    def generate_matches(self, matches_configuration: list[MatchSuggestion]) -> None:
        sugested_matches = [
            LeagueSuggestedMatch(**match_data.__dict__)
            for match_data in matches_configuration
        ]

        # validate the matches configuration before creating matches
        self._check_matches_configuration(sugested_matches)

        for suggested_match in sugested_matches:
            match = create_match(
                tournament_id=self.tournament.id,
                participants=suggested_match.competitors_ids,
            )

            LeagueMatch.objects.create(
                match=match, round_number=suggested_match.round_number
            )
