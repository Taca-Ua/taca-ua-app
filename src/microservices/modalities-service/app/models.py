"""
SQLAlchemy models for Modalities Service.
Schema: modalities
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import ARRAY, JSON, Boolean, Column, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ModalityType(enum.Enum):
    """Enum for modality types"""

    COLETIVA = "coletiva"
    INDIVIDUAL = "individual"
    MISTA = "mista"


class Course(Base):
    """
    Represents an academic course.
    """

    __tablename__ = "course"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    abbreviation = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Course {self.id} - {self.abbreviation}: {self.name}>"


class Modality(Base):
    """
    Represents a sport modality.
    """

    __tablename__ = "modality"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    type = Column(Enum(ModalityType), nullable=False)
    scoring_schema = Column(JSON, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Modality {self.id} - {self.name} ({self.type.value})>"


class Team(Base):
    """
    Represents a team for a modality and course.
    """

    __tablename__ = "team"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modality_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(Text, nullable=False)
    players = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Team {self.id} - {self.name}>"


class Student(Base):
    """
    Represents a student.
    """

    __tablename__ = "student"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    full_name = Column(Text, nullable=False)
    student_number = Column(Text, nullable=False, unique=True)
    email = Column(Text, nullable=True)
    is_member = Column(Boolean, nullable=False, default=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Student {self.id} - {self.full_name} ({self.student_number})>"
