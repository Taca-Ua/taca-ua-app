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
from sqlalchemy.orm import relationship
from taca_outbox.models import create_outbox_model

Base = declarative_base()


class MatchStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class ParticipantType(enum.Enum):
    TEAM = "team"
    ATHLETE = "athlete"


class Match(Base):
    """
    A single competitive occurrence.
    No assumptions about sport, modality, or structure.
    """

    __tablename__ = "match"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Optional reference to tournament domain
    tournament_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    location = Column(Text, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)

    status = Column(
        Enum(MatchStatus, name="match_status"),
        nullable=False,
        default=MatchStatus.SCHEDULED,
    )

    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )

    participants = relationship(
        "MatchParticipant",
        back_populates="match",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Match {self.id} status={self.status.value}>"


class MatchParticipant(Base):
    """
    Represents one participant in a match and its outcome.
    """

    __tablename__ = "match_participant"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("matches.match.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    participant_type = Column(
        Enum(ParticipantType, name="participant_type"),
        nullable=False,
    )

    # External references
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    athlete_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Outcome
    score = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)

    # Escape hatch for sport-specific facts
    result_metadata = Column(JSON, nullable=True)

    match = relationship("Match", back_populates="participants")

    def __repr__(self) -> str:
        return f"<MatchParticipant match={self.match_id}>"


class Lineup(Base):
    """
    Stores lineup / roster information for team-based matches.
    """

    __tablename__ = "lineup"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("matches.match.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Team Service reference
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Student / Athlete Service reference
    player_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    jersey_number = Column(Integer, nullable=False)
    is_starter = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Lineup match={self.match_id} player={self.player_id}>"


class Comment(Base):
    """
    Commentary or notes attached to a match.
    """

    __tablename__ = "comment"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("matches.match.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


# OutboxEvent model — schema-bound via shared factory
OutboxEvent = create_outbox_model(Base, schema="matches")
