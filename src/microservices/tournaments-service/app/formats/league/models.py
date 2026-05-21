"""
League format specific models for standings and match results.
These are separate from the core models to avoid cluttering the main tournament and match schemas with format-specific fields.
"""

from typing import List

import sqlalchemy as sa
from app.models import Base, Tournament
from sqlalchemy import JSON, UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship


class ScoreDifferenceTiebreakerPolicy:
    NONE = "none"
    POINTS_DIFFERENCE = "points_difference"
    SCORED_POINTS = "scored_points"

    def __init__(self, value):
        if value not in [self.NONE, self.POINTS_DIFFERENCE, self.SCORED_POINTS]:
            raise ValueError(f"Invalid tiebreaker policy: {value}")
        self.value = value


class LeagueTournament(Tournament):
    __tablename__ = "league_tournaments"
    __table_args__ = (
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["id"], ["tournaments.tournament.id"], ondelete="CASCADE"
        ),
        {"schema": "tournaments"},
    )
    __mapper_args__ = {
        "polymorphic_identity": "league",
    }

    id = Column(
        UUID(as_uuid=True), ForeignKey("tournaments.tournament.id"), primary_key=True
    )

    # Points awarded for each match outcome
    points_win = Column(Integer, default=3)
    points_draw = Column(Integer, default=1)
    points_loss = Column(Integer, default=0)

    # Track the current round of the league for scheduling purposes
    current_round = Column(Integer, default=1)
    points_diff_tiebreaker = Column(
        String, default=ScoreDifferenceTiebreakerPolicy.POINTS_DIFFERENCE
    )

    league_standings: Mapped[List["LeagueStandings"]] = relationship(
        "LeagueStandings", back_populates="tournament", cascade="all, delete-orphan"
    )
    league_matches: Mapped[List["LeagueMatches"]] = relationship(
        "LeagueMatches", back_populates="tournament", cascade="all, delete-orphan"
    )

    def to_dict(self, include_teams=False, include_ranking=False):
        base = super().to_dict(include_teams, include_ranking)

        league_data = {
            "points_win": self.points_win,
            "points_draw": self.points_draw,
            "points_loss": self.points_loss,
            "current_round": self.current_round,
            "points_diff_tiebreaker": self.points_diff_tiebreaker,
        }
        base["format_data"] = league_data
        return base


class LeagueStandings(Base):
    __tablename__ = "league_standings"
    __table_args__ = (
        sa.PrimaryKeyConstraint("tournament_id", "competitor_id"),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["tournaments.league_tournaments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["competitor_id"],
            ["tournaments.tournament_competitor.id"],
            ondelete="CASCADE",
        ),
        {"schema": "tournaments"},
    )

    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.league_tournaments.id"),
        nullable=False,
        primary_key=True,
    )
    competitor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.tournament_competitor.id"),
        nullable=False,
        primary_key=True,
    )

    points = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)

    scored_points = Column(Integer, default=0)
    conceded_points = Column(Integer, default=0)

    tournament: Mapped[LeagueTournament] = relationship(
        "LeagueTournament", back_populates="league_standings"
    )
    # competitor: Mapped[TournamentCompetitor] = relationship("TournamentCompetitor", back_populates="league_standings")


class LeagueMatches(Base):
    __tablename__ = "league_matches"
    __table_args__ = (
        sa.PrimaryKeyConstraint("tournament_id", "match_id"),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["tournaments.league_tournaments.id"], ondelete="CASCADE"
        ),
        {"schema": "tournaments"},
    )

    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.league_tournaments.id"),
        nullable=False,
        primary_key=True,
    )
    match_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)

    # Store match results relevant to this config: {"competitorA_id": {"score": <score>, "position": <position>, "result": <result> }, "competitorB_id": {"score": <score>, "position": <position>, "result": <result>}}
    results = Column(JSON, nullable=True)

    tournament: Mapped[LeagueTournament] = relationship(
        "LeagueTournament", back_populates="league_matches"
    )
