"""
SQLAlchemy models for Read Model tables.

This package contains models for both:
1. Source schemas (matches, tournaments, modalities, ranking) - READ ONLY
2. public_read schema - READ/WRITE

These models can be shared across services that need read access.
"""

import enum

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID

from .metadata import Base


class GameState(enum.Enum):
    """Enum for game states"""

    SCHEDULED = "scheduled"
    FINISHED = "finished"
    CANCELED = "canceled"


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
