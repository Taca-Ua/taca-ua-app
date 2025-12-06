"""
SQLAlchemy models for Ranking Service.
Schema: ranking
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ModalityRanking(Base):
    """
    Represents rankings for a modality (sport) in a season.
    Aggregates team/course performance across all tournaments of this modality.
    """

    __tablename__ = "modality_ranking"
    __table_args__ = {"schema": "ranking"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modality_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    season_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    points = Column(Float, nullable=False, default=0.0)
    details = Column(JSON, nullable=True)  # Additional ranking details
    last_updated = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<ModalityRanking {self.id} - Course {self.course_id} in Modality {self.modality_id}: {self.points} pts>"


class CourseRanking(Base):
    """
    Represents overall rankings for a course in a season.
    Aggregates points from all modalities.
    """

    __tablename__ = "course_ranking"
    __table_args__ = {"schema": "ranking"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    season_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    total_points = Column(Float, nullable=False, default=0.0)
    modality_breakdown = Column(JSON, nullable=True)  # Points per modality
    last_updated = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<CourseRanking {self.id} - Course {self.course_id}: {self.total_points} pts>"


class GeneralRanking(Base):
    """
    Represents the general/overall ranking across all courses.
    This is a denormalized view for quick access.
    """

    __tablename__ = "general_ranking"
    __table_args__ = {"schema": "ranking"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    total_points = Column(Float, nullable=False, default=0.0)
    last_updated = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<GeneralRanking {self.id} - Position {self.position}: Course {self.course_id} ({self.total_points} pts)>"
