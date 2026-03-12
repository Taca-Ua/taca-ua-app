"""
SQLAlchemy models for Ranking Service.
Schema: ranking
"""

from sqlalchemy import ARRAY, UUID, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from taca_outbox.models import create_outbox_model

Base = declarative_base()


# OutboxEvent model — schema-bound via shared factory
OutboxEvent = create_outbox_model(Base, schema="ranking")


# Core tables populated by event handlers
class ModalityTypeEscalao(Base):
    __tablename__ = "modality_type_escaloes"
    __table_args__ = {"schema": "ranking"}

    _id = Column(Integer, primary_key=True, autoincrement=True)
    modality_type_id = Column(UUID(as_uuid=True))
    min_participants = Column(Integer, nullable=True)
    max_participants = Column(Integer, nullable=True)
    points = Column(ARRAY(Integer), nullable=False)


class ModalityType(Base):
    __tablename__ = "modality_types"
    __table_args__ = {"schema": "ranking"}
    modality_type_id = Column(UUID(as_uuid=True), primary_key=True)


class Modality(Base):
    __tablename__ = "modalities"
    __table_args__ = {"schema": "ranking"}

    modality_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_type_id = Column(UUID(as_uuid=True), nullable=False)


class Tournament(Base):
    __tablename__ = "tournaments"
    __table_args__ = {"schema": "ranking"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    scoring_format_id = Column(UUID(as_uuid=True), nullable=True)


class TournamentCompetitor(Base):
    __tablename__ = "tournament_competitors"
    __table_args__ = {"schema": "ranking"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    competitor_id = Column(UUID(as_uuid=True), primary_key=True)


class TournamentResult(Base):
    __tablename__ = "tournament_results"
    __table_args__ = {"schema": "ranking"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    competitor_id = Column(UUID(as_uuid=True), primary_key=True)
    position = Column(Integer, nullable=False)


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = {"schema": "ranking"}

    course_id = Column(UUID(as_uuid=True), primary_key=True)


# Derived tables
class GeneralRanking(Base):
    __tablename__ = "general_rankings"
    __table_args__ = {"schema": "ranking"}

    course_id = Column(UUID(as_uuid=True), primary_key=True)
    points = Column(Integer, nullable=False)


class ModalityRanking(Base):
    __tablename__ = "modality_rankings"
    __table_args__ = {"schema": "ranking"}

    modality_id = Column(UUID(as_uuid=True), primary_key=True)
    course_id = Column(UUID(as_uuid=True), primary_key=True)
    points = Column(Integer, nullable=False)


class CourseRanking(Base):
    __tablename__ = "course_rankings"
    __table_args__ = {"schema": "ranking"}

    course_id = Column(UUID(as_uuid=True), primary_key=True)
    points = Column(Integer, nullable=False)
    modality_breakdown = Column(ARRAY(Integer), nullable=False)  # Points per modality
