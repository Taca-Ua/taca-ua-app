"""
SQLAlchemy models for Ranking Service.
Schema: ranking
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TeamRanking(Base):
    """
    Represents a team's ranking in a tournament.
    This is recalculated based on result.submitted events.
    """

    __tablename__ = "team_ranking"
    __table_args__ = {"schema": "ranking"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    wins = Column(Integer, nullable=False, default=0)
    draws = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    goals_for = Column(Integer, nullable=False, default=0)
    goals_against = Column(Integer, nullable=False, default=0)
    points = Column(Integer, nullable=False, default=0)
    last_updated = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<TeamRanking {self.id} - Team {self.team_id} in Tournament {self.tournament_id}: {self.points} pts>"
