"""
SQLAlchemy models for Matches Service.
Schema: matches
"""

import enum
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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


class OutboxEvent(Base):
    """
    Outbox pattern for reliable event publishing.
    Events are stored here first, then published by the OutboxPublisher.
    """

    __tablename__ = "outbox_event"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(
        String(255), nullable=False, index=True
    )  # e.g., 'match.created'
    aggregate_type = Column(String(100), nullable=False, index=True)  # e.g., 'match'
    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payload = Column(JSON, nullable=False)  # Event data
    published = Column(Boolean, default=False, nullable=False, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    retry_count = Column(sa.Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": str(self.aggregate_id),
            "payload": self.payload,
            "published": self.published,
            "published_at": (
                self.published_at.isoformat() if self.published_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "retry_count": self.retry_count,
            "last_error": self.last_error,
        }
