"""
SQLAlchemy models for Matches Service.
Schema: matches
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GameState(enum.Enum):
    """Enum for game states"""

    SCHEDULED = "scheduled"
    FINISHED = "finished"
    CANCELED = "canceled"


class Game(Base):
    """
    Represents a game/match in a tournament.
    """

    __tablename__ = "game"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    modality_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    team_a_id = Column(UUID(as_uuid=True), nullable=False)
    team_b_id = Column(UUID(as_uuid=True), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    location = Column(Text)
    state = Column(Enum(GameState), nullable=False, default=GameState.SCHEDULED)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Game {self.id} - {self.state.value}>"


class Result(Base):
    """
    Stores the result of a game.
    Separated from Game to allow historical editing and auditing.
    """

    __tablename__ = "result"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(
        UUID(as_uuid=True), ForeignKey("matches.game.id"), nullable=False, index=True
    )
    team_a_score = Column(Integer, nullable=False)
    team_b_score = Column(Integer, nullable=False)
    submitted_by = Column(UUID(as_uuid=True), nullable=False)
    submitted_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Result {self.id} - Game {self.game_id}: {self.team_a_score}-{self.team_b_score}>"
