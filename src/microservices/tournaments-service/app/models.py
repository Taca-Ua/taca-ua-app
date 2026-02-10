"""
SQLAlchemy models for Tournaments Service.
Schema: tournaments
"""

import enum
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import (
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


class CompetitorType(enum.Enum):
    TEAM = "team"
    ATHLETE = "athlete"


class TournamentCompetitor(Base):
    """
    A competitor subscribed to a tournament.
    Can be a team or an individual athlete.
    """

    __tablename__ = "tournament_competitor"
    __table_args__ = {"schema": "tournaments"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.tournament.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    competitor_type = Column(
        Enum(CompetitorType, name="competitor_type"),
        nullable=False,
    )

    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    athlete_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    tournament = relationship("Tournament", back_populates="competitors")

    def to_dict(self):
        resp = {
            "id": str(self.id),
            "tournament_id": str(self.tournament_id),
            "competitor_type": self.competitor_type.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if self.competitor_type == CompetitorType.TEAM:
            resp["competitor"] = {"team_id": str(self.team_id)}
        else:
            resp["competitor"] = {"athlete_id": str(self.athlete_id)}

        return resp


class Tournament(Base):
    """Represents a tournament"""

    __tablename__ = "tournament"
    __table_args__ = {"schema": "tournaments"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modality_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(Text, nullable=False)
    status = Column(
        String(20), nullable=False, default="draft", index=True
    )  # draft, active, finished
    start_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)
    finished_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    ranking_positions = relationship(
        "TournamentRankingPosition",
        back_populates="tournament",
        cascade="all, delete-orphan",
    )
    competitors = relationship(
        "TournamentCompetitor",
        back_populates="tournament",
        cascade="all, delete-orphan",
    )

    def to_dict(self, include_teams=False, include_ranking=False):
        result = {
            "id": str(self.id),
            "modality_id": str(self.modality_id),
            "name": self.name,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "finished_by": str(self.finished_by) if self.finished_by else None,
            "competitors": [comp.to_dict() for comp in self.competitors],
        }

        if include_ranking:
            result["ranking_positions"] = [
                rp.to_dict() for rp in self.ranking_positions
            ]

        return result


class TournamentRankingPosition(Base):
    """Represents the ranking position of a team in a tournament"""

    __tablename__ = "tournament_ranking_position"
    __table_args__ = (
        sa.UniqueConstraint("tournament_id", "team_id", name="uq_tournament_team"),
        {"schema": "tournaments"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.tournament.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    tournament = relationship("Tournament", back_populates="ranking_positions")

    def to_dict(self):
        return {
            "id": str(self.id),
            "tournament_id": str(self.tournament_id),
            "team_id": str(self.team_id),
            "position": self.position,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class OutboxEvent(Base):
    """
    Outbox pattern for reliable event publishing.
    Events are stored here first, then published by the OutboxPublisher.
    """

    __tablename__ = "outbox_event"
    __table_args__ = {"schema": "tournaments"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(
        String(255), nullable=False, index=True
    )  # e.g., 'tournament.created'
    aggregate_type = Column(
        String(100), nullable=False, index=True
    )  # e.g., 'tournament'
    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payload = Column(sa.JSON, nullable=False)  # Event data
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
