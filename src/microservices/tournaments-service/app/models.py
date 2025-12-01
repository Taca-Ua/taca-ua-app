"""
SQLAlchemy models for Tournaments Service.
Schema: tournaments
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TournamentType(enum.Enum):
    """Enum for tournament types"""

    ROUND_ROBIN = "round_robin"
    ELIMINATION = "elimination"
    GROUPS = "groups"


class Tournament(Base):
    """
    Represents a tournament.
    """

    __tablename__ = "tournament"
    __table_args__ = {"schema": "tournaments"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modality_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(Text, nullable=False)
    type = Column(Enum(TournamentType), nullable=False)
    season = Column(Integer, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Tournament {self.id} - {self.name} ({self.season})>"


class Stage(Base):
    """
    Represents a stage within a tournament (e.g., group stage, playoffs).
    """

    __tablename__ = "stage"
    __table_args__ = {"schema": "tournaments"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.tournament.id"),
        nullable=False,
        index=True,
    )
    name = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Stage {self.id} - {self.name} (Order: {self.order})>"


class Journey(Base):
    """
    Represents a journey/round within a stage (e.g., matchday, round).
    """

    __tablename__ = "journey"
    __table_args__ = {"schema": "tournaments"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.stage.id"),
        nullable=False,
        index=True,
    )
    number = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Journey {self.id} - Number {self.number}>"
