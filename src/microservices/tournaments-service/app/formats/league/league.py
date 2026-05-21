"""
League format tournament engine.

Implements round-robin tournament progression where:
- Each competitor plays against each other competitor once per round (if configured)
- Standings are calculated based on win/draw/loss points
- Scoring rules are configurable per tournament
"""

from typing import Any, Dict, List

from app.logger import logger
from app.models import Tournament, TournamentCompetitor
from sqlalchemy import UUID
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.matches import (
    MatchCreatedV1,
    MatchDeletedV1,
    MatchResultUpdatedV1,
)

from ..base import FormatEngine, FormatStandings
from .models import (
    LeagueMatches,
    LeagueStandings,
    LeagueTournament,
    ScoreDifferenceTiebreakerPolicy,
)


class LeagueFormatEngine(FormatEngine):
    """
    Round-robin league format engine.

    Configuration format (tournament.format_config):
    {
        "win_points": 3,
        "draw_points": 1,
        "loss_points": 0,
        "matches_per_round": null  # null = all competitors play in round, or specify fixed number
    }
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize league engine with scoring rules.

        Args:
            config: Optional dict with scoring configuration.
                   Defaults: win=3, draw=1, loss=0
        """
        if config is None:
            config = {}

        self.win_points = config.get("win_points", 3)
        self.draw_points = config.get("draw_points", 1)
        self.loss_points = config.get("loss_points", 0)

    @property
    def format_name(self) -> str:
        return "league"

    def complete_tournament(
        self, tournament: Tournament, format_data: Dict[str, Any]
    ) -> None:
        # validate format_data
        print(f"Completing tournament with format_data: {format_data}", flush=True)
        if not isinstance(format_data, dict):
            raise ValueError("format_data must be a dictionary for league format")
        if "win_points" not in format_data or not isinstance(
            format_data["win_points"], int
        ):
            raise ValueError("win_points must be an integer")
        if "draw_points" not in format_data or not isinstance(
            format_data["draw_points"], int
        ):
            raise ValueError("draw_points must be an integer")
        if "loss_points" not in format_data or not isinstance(
            format_data["loss_points"], int
        ):
            raise ValueError("loss_points must be an integer")
        if "points_diff_tiebreaker" in format_data:
            ScoreDifferenceTiebreakerPolicy(
                format_data["points_diff_tiebreaker"]
            )  # validate tiebreaker value

        print(f"Validated format_data: {format_data}", flush=True)

        # configure tournament with league-specific settings
        tournament: LeagueTournament = tournament  # type cast for clarity
        tournament.points_win = format_data.get("win_points", self.win_points)
        tournament.points_draw = format_data.get("draw_points", self.draw_points)
        tournament.points_loss = format_data.get("loss_points", self.loss_points)
        tournament.current_round = 1

        # Set tiebreaker policy, defaulting to points difference if not specified
        if format_data.get("points_diff_tiebreaker"):
            tournament.points_diff_tiebreaker = format_data["points_diff_tiebreaker"]

        return tournament

    def update_tournament(
        self, tournament: Tournament, format_data: Dict[str, Any]
    ) -> None:
        # allow updating scoring rules mid-tournament if needed
        if not isinstance(format_data, dict):
            raise ValueError(
                f"format_data must be a dictionary for league format. Payload received: {format_data}"
            )
        if "win_points" not in format_data or not isinstance(
            format_data["win_points"], int
        ):
            raise ValueError(
                f"win_points must be an integer. Payload received: {format_data}"
            )
        if "draw_points" not in format_data or not isinstance(
            format_data["draw_points"], int
        ):
            raise ValueError(
                f"draw_points must be an integer. Payload received: {format_data}"
            )
        if "loss_points" not in format_data or not isinstance(
            format_data["loss_points"], int
        ):
            raise ValueError(
                f"loss_points must be an integer. Payload received: {format_data}"
            )
        if "points_diff_tiebreaker" in format_data:
            ScoreDifferenceTiebreakerPolicy(
                format_data["points_diff_tiebreaker"]
            )  # validate tiebreaker value

        # Update tournament scoring rules
        tournament: LeagueTournament = tournament  # type cast for clarity
        tournament.points_win = format_data.get("win_points", tournament.points_win)
        tournament.points_draw = format_data.get("draw_points", tournament.points_draw)
        tournament.points_loss = format_data.get("loss_points", tournament.points_loss)
        if format_data.get("points_diff_tiebreaker"):
            tournament.points_diff_tiebreaker = format_data["points_diff_tiebreaker"]

        # Recalculate standings for all competitors based on new scoring rules
        for standing in tournament.league_standings:
            # Recalculate points based on wins/draws/losses and new scoring rules
            standing.points = (
                standing.wins * tournament.points_win
                + standing.draws * tournament.points_draw
                + standing.losses * tournament.points_loss
            )

    def on_competitor_added(
        self, db: Session, tournament_competitor: TournamentCompetitor
    ):
        """Handle logic when a competitor is added to a league tournament."""
        new_standing = LeagueStandings(
            tournament_id=tournament_competitor.tournament_id,
            competitor_id=tournament_competitor.id,
            points=0,
            wins=0,
            draws=0,
            losses=0,
        )
        db.add(new_standing)
        db.flush()

    def on_competitor_removed(
        self, db: Session, tournament_competitor: TournamentCompetitor
    ):
        """Handle logic when a competitor is removed from a league tournament."""
        db.query(LeagueStandings).filter(
            LeagueStandings.tournament_id == tournament_competitor.tournament_id,
            LeagueStandings.competitor_id == tournament_competitor.id,
        ).delete()
        db.flush()

    # Event handlers for match events to update league standings
    def event_handle_match_created(self, db: Session, event_data: MatchCreatedV1):
        """
        Handle match created event for league format.

        Initializes match config record for the new match.
        """
        tournament_id = event_data.data.tournament_id
        match_id = event_data.data.match_id

        # Create a new LeagueMatches record for this match
        league_match = LeagueMatches(
            tournament_id=tournament_id,
            match_id=match_id,
            results=None,  # No results yet
        )
        db.add(league_match)
        db.flush()  # Flush to get ID if needed

    def event_handle_match_deleted(self, db: Session, event: MatchDeletedV1):
        """
        Handle match deleted event for league format.

        Cleans up any league-specific records related to the deleted match.
        """
        match_id = event.data.match_id

        # Delete the LeagueMatches record associated with this match
        match = (
            db.query(LeagueMatches).filter(LeagueMatches.match_id == match_id).first()
        )
        if not match:
            logger.warning(
                f"No LeagueMatches record found for match_id {match_id}, skipping deletion"
            )
            return

        db.query(LeagueMatches).filter(LeagueMatches.match_id == match_id).delete()
        db.flush()

    def event_handle_match_result_updated(
        self, db: Session, event: MatchResultUpdatedV1
    ):
        """
        Handle match result updated event for league format.

        Updates the league standings based on the new match result.
        """
        match_id = event.data.match_id
        results = event.data.results

        # Update the LeagueMatches record with the new results
        match = (
            db.query(LeagueMatches).filter(LeagueMatches.match_id == match_id).first()
        )
        if not match:
            logger.warning(
                f"No LeagueMatches record found for match_id {match_id}, cannot update results"
            )
            return

        participant_results_map = {}

        # Determine match result for each competitor based on scores
        if all(r.score is not None for r in results):
            # score-based result calculation.
            # Most points wins, ties if all competitors have same points

            max_score = max(r.score for r in results)
            winners = [r for r in results if r.score == max_score]
            if len(winners) == 1:
                # Clear winner
                for r in results:
                    if r == winners[0]:
                        participant_results_map[r.participant_id] = "win"
                    else:
                        participant_results_map[r.participant_id] = "loss"
            else:
                # Tie between all competitors with biggest score, everyone else loses
                for r in results:
                    if r.score == max_score:
                        participant_results_map[r.participant_id] = "draw"
                    else:
                        participant_results_map[r.participant_id] = "loss"

        elif all(r.position is not None for r in results):
            # position-based result calculation.
            # First place wins, ties if multiple competitors share first place, everyone else loses

            min_position = min(r.position for r in results)
            winners = [r for r in results if r.position == min_position]
            if len(winners) == 1:
                # Clear winner
                for r in results:
                    if r == winners[0]:
                        participant_results_map[r.participant_id] = "win"
                    else:
                        participant_results_map[r.participant_id] = "loss"
            else:
                # Tie between all competitors with best position, everyone else loses
                for r in results:
                    if r.position == min_position:
                        participant_results_map[r.participant_id] = "draw"
                    else:
                        participant_results_map[r.participant_id] = "loss"
        else:
            logger.warning(
                f"Cannot determine match result for match_id {match_id} due to missing scores and positions. Results received: {results}"
            )
            return

        # Update the match record with the new results
        match.results = {
            str(r.participant_id): {
                "score": r.score,
                "position": r.position,
                "result": participant_results_map[r.participant_id],
            }
            for r in results
        }

        for participant_id, result in participant_results_map.items():
            # Update standings for each participant based on their result
            standing = (
                db.query(LeagueStandings)
                .filter(
                    LeagueStandings.tournament_id == match.tournament_id,
                    LeagueStandings.competitor_id == participant_id,
                )
                .first()
            )

            if not standing:
                logger.warning(
                    f"No LeagueStandings record found for competitor_id {participant_id} in tournament_id {match.tournament_id}, skipping standings update"
                )
                continue

            if result == "win":
                standing.points += match.tournament.points_win
                standing.wins += 1
            elif result == "draw":
                standing.points += match.tournament.points_draw
                standing.draws += 1
            elif result == "loss":
                standing.points += match.tournament.points_loss
                standing.losses += 1

            # Update scored and conceded points if score information is available
            scored_points = match.results[str(participant_id)]["score"] or 0
            standing.scored_points += scored_points

            conceded_points = sum(
                r.score or 0 for r in results if r.participant_id != participant_id
            )
            standing.conceded_points += conceded_points

        db.flush()

    # Utility methods
    def get_standings(self, db: Session, tournament_id: UUID) -> List[FormatStandings]:
        """
        Get the current standings for a league tournament.

        Returns a list of FormatStandings objects.
        """
        standings_stmt = db.query(LeagueStandings).filter(
            LeagueStandings.tournament_id == tournament_id
        )

        tourn = (
            db.query(LeagueTournament)
            .filter(LeagueTournament.id == tournament_id)
            .first()
        )
        if not tourn:
            logger.warning(
                f"No standings found for tournament_id {tournament_id}, returning empty standings list"
            )
            return []

        # Order standings based on points and tiebreaker policy
        standings_stmt = standings_stmt.order_by(LeagueStandings.points.desc())
        if (
            tourn.points_diff_tiebreaker
            == ScoreDifferenceTiebreakerPolicy.POINTS_DIFFERENCE
        ):
            standings_stmt = standings_stmt.order_by(
                (
                    LeagueStandings.scored_points - LeagueStandings.conceded_points
                ).desc(),
                LeagueStandings.scored_points.desc(),
            )
        elif (
            tourn.points_diff_tiebreaker
            == ScoreDifferenceTiebreakerPolicy.SCORED_POINTS
        ):
            standings_stmt = standings_stmt.order_by(
                LeagueStandings.scored_points.desc(),
            )
        elif tourn.points_diff_tiebreaker == ScoreDifferenceTiebreakerPolicy.NONE:
            pass  # no additional ordering, competitors with same points will share position

        standings = standings_stmt.all()

        # Calculate position
        postition_standings: List[LeagueStandings] = []
        current_position = 1
        last_points = None
        last_scored_conceded_diff = None
        last_scored = None
        for i, s in enumerate(standings, start=1):
            if last_points is not None and (s.points < last_points):
                current_position = (
                    i  # update position if points are lower than previous competitor
                )
            elif last_points is not None and s.points == last_points:

                # If points are the same, check tiebreaker policy
                if (
                    s.tournament.points_diff_tiebreaker
                    == ScoreDifferenceTiebreakerPolicy.NONE
                ):
                    pass  # no tiebreaker, competitors with same points share the same position

                elif (
                    s.tournament.points_diff_tiebreaker
                    == ScoreDifferenceTiebreakerPolicy.POINTS_DIFFERENCE
                ):
                    scored_conceded_diff = s.scored_points - s.conceded_points
                    if (
                        last_scored_conceded_diff is not None
                        and scored_conceded_diff < last_scored_conceded_diff
                    ):
                        current_position = i  # update position if points difference is lower than previous competitor

                elif (
                    s.tournament.points_diff_tiebreaker
                    == ScoreDifferenceTiebreakerPolicy.SCORED_POINTS
                ):
                    if last_scored is not None and s.scored_points < last_scored:
                        current_position = i  # update position if scored points is lower than previous competitor

            last_points = s.points
            last_scored_conceded_diff = s.scored_points - s.conceded_points
            last_scored = s.scored_points

            postition_standings.append(
                FormatStandings(
                    competitor_id=str(s.competitor_id),
                    position=current_position,
                    format_meta={
                        "points": s.points,
                        "wins": s.wins,
                        "draws": s.draws,
                        "losses": s.losses,
                        "scored_points": s.scored_points,
                        "conceded_points": s.conceded_points,
                        "differential": s.scored_points - s.conceded_points,
                    },
                )
            )

        return postition_standings
