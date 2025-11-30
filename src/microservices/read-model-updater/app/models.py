"""
SQLAlchemy models for Read Model Updater Service.

This service listens to events from other microservices and updates
the read-only views in the public_read schema.

It needs access to both:
1. Source schemas (matches, tournaments, modalities, ranking) - READ ONLY
2. public_read schema - READ/WRITE
"""

import enum

from sqlalchemy import Column, DateTime, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Re-export models from other services for read access
# In a real implementation, you would import these directly from the service packages


class GameState(enum.Enum):
    """Enum for game states"""

    SCHEDULED = "scheduled"
    FINISHED = "finished"
    CANCELED = "canceled"


# Source models (READ ONLY) - for querying
class Game(Base):
    """Read-only access to matches.game"""

    __tablename__ = "game"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_id = Column(UUID(as_uuid=True))
    modality_id = Column(UUID(as_uuid=True))
    team_a_id = Column(UUID(as_uuid=True))
    team_b_id = Column(UUID(as_uuid=True))
    scheduled_at = Column(DateTime)
    location = Column(Text)
    state = Column(Enum(GameState))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Result(Base):
    """Read-only access to matches.result"""

    __tablename__ = "result"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    game_id = Column(UUID(as_uuid=True))
    team_a_score = Column(Integer)
    team_b_score = Column(Integer)
    submitted_by = Column(UUID(as_uuid=True))
    submitted_at = Column(DateTime)


class Tournament(Base):
    """Read-only access to tournaments.tournament"""

    __tablename__ = "tournament"
    __table_args__ = {"schema": "tournaments"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(UUID(as_uuid=True))
    name = Column(Text)
    type = Column(Text)
    season = Column(Integer)
    created_at = Column(DateTime)


class Modality(Base):
    """Read-only access to modalities.modality"""

    __tablename__ = "modality"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text)
    description = Column(Text)


class TeamRanking(Base):
    """Read-only access to ranking.team_ranking"""

    __tablename__ = "team_ranking"
    __table_args__ = {"schema": "ranking"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_id = Column(UUID(as_uuid=True))
    team_id = Column(UUID(as_uuid=True))
    wins = Column(Integer)
    draws = Column(Integer)
    losses = Column(Integer)
    goals_for = Column(Integer)
    goals_against = Column(Integer)
    points = Column(Integer)
    last_updated = Column(DateTime)


# Target models (READ/WRITE) - for updating views
class GamesView(Base):
    """Writable projection for public_read.games_view"""

    __tablename__ = "games_view"
    __table_args__ = {"schema": "public_read"}

    game_id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_name = Column(Text)
    modality_name = Column(Text)
    team_a_name = Column(Text)
    team_b_name = Column(Text)
    score = Column(Text)
    scheduled_at = Column(DateTime)
    state = Column(Text)


class TournamentView(Base):
    """Writable projection for public_read.tournament_view"""

    __tablename__ = "tournament_view"
    __table_args__ = {"schema": "public_read"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text)
    modality = Column(Text)
    stage_count = Column(Integer)
    total_matches = Column(Integer)


class RankingView(Base):
    """Writable projection for public_read.ranking_view"""

    __tablename__ = "ranking_view"
    __table_args__ = {"schema": "public_read"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    team = Column(Text, primary_key=True)
    points = Column(Integer)
    position = Column(Integer)
