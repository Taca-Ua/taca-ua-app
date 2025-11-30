"""
SQLAlchemy models for Public API - Read Model.
Schema: public_read

These are projection views updated by the Read Model Updater service.
Public API only reads from these views, never writes.
"""

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GamesView(Base):
    """
    Read-only view of games with joined tournament, modality, and team information.
    Updated by Read Model Updater.
    """

    __tablename__ = "games_view"
    __table_args__ = {"schema": "public_read"}

    game_id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_name = Column(Text)
    modality_name = Column(Text)
    team_a_name = Column(Text)
    team_b_name = Column(Text)
    score = Column(Text)  # Format: "1-0" or "2-2"
    scheduled_at = Column(DateTime)
    state = Column(Text)

    def __repr__(self):
        return f"<GamesView {self.game_id} - {self.team_a_name} vs {self.team_b_name}: {self.score}>"


class TournamentView(Base):
    """
    Read-only consolidated view of tournament information.
    Updated by Read Model Updater.
    """

    __tablename__ = "tournament_view"
    __table_args__ = {"schema": "public_read"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text)
    modality = Column(Text)
    stage_count = Column(Integer)
    total_matches = Column(Integer)

    def __repr__(self):
        return f"<TournamentView {self.tournament_id} - {self.name}>"


class RankingView(Base):
    """
    Read-only view of team rankings in tournaments.
    Updated by Read Model Updater.
    """

    __tablename__ = "ranking_view"
    __table_args__ = {"schema": "public_read"}

    # Using a composite primary key approach
    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    team = Column(Text, primary_key=True)
    points = Column(Integer)
    position = Column(Integer)

    def __repr__(self):
        return f"<RankingView Tournament {self.tournament_id} - {self.team}: Position {self.position}>"
