"""
SQLAlchemy models for Matches Service.
Schema: matches
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MatchStatus(enum.Enum):
    """Enum for match status"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Match(Base):
    """
    Represents a match/game in a tournament.
    """

    __tablename__ = "match"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    team_home_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    team_away_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    location = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    status = Column(Enum(MatchStatus), nullable=False, default=MatchStatus.SCHEDULED)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    additional_details = Column(JSON, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Match {self.id} - {self.status.value}>"


class Lineup(Base):
    """
    Stores lineup/roster information for a match.
    """

    __tablename__ = "lineup"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(
        UUID(as_uuid=True), ForeignKey("matches.match.id"), nullable=False, index=True
    )
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    player_id = Column(UUID(as_uuid=True), nullable=False)
    jersey_number = Column(Integer, nullable=False)
    is_starter = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Lineup {self.id} - Match {self.match_id}, Player {self.player_id}>"


class Comment(Base):
    """
    Stores comments for a match.
    """

    __tablename__ = "comment"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(
        UUID(as_uuid=True), ForeignKey("matches.match.id"), nullable=False, index=True
    )
    message = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Comment {self.id} - Match {self.match_id}>"
