"""
SQLAlchemy models for Public API - Read Model.

These are projection views managed by a main api worker.
These SQLAlchemy models should reflect the Django models defined in the projections app of the competition-api-v3.
"""

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TeamDetailView(Base):
    """Materialized view: Team with course, nucleo, and modality details."""

    __tablename__ = "projections_teamdetailview"

    team_id = Column(UUID, primary_key=True)
    team_name = Column(String(255))
    team_season_id = Column(Integer)

    course_id = Column(UUID)
    course_name = Column(String(255))
    course_abbreviation = Column(String(255))

    nucleo_id = Column(UUID)
    nucleo_name = Column(String(255))
    nucleo_abbreviation = Column(String(255))
    nucleo_logo_url = Column(String(255))

    modality_id = Column(UUID)
    modality_name = Column(String(255))
    modality_type_id = Column(UUID)
    modality_type_name = Column(String(255))

    player_count = Column(Integer)
    players = Column(JSON)


class StudentDetailView(Base):
    """Materialized view: Student with course and nucleo details."""

    __tablename__ = "projections_studentdetailview"

    student_id = Column(UUID, primary_key=True)
    student_number = Column(String(255))
    full_name = Column(String(255))
    is_member = Column(Boolean)

    course_id = Column(UUID)
    course_name = Column(String(255))
    course_abbreviation = Column(String(255))

    nucleo_id = Column(UUID)
    nucleo_name = Column(String(255))
    nucleo_abbreviation = Column(String(255))

    team_count = Column(Integer)


class TournamentDetailView(Base):
    """Materialized view: Tournament with modality and competitor details."""

    __tablename__ = "projections_tournamentdetailview"

    tournament_id = Column(UUID, primary_key=True)
    tournament_name = Column(String(255))
    tournament_season_id = Column(Integer)
    start_date = Column(Date)
    status = Column(String(255))

    modality_id = Column(UUID)
    modality_name = Column(String(255))
    modality_type_id = Column(UUID)
    modality_type_name = Column(String(255))

    competitor_count = Column(Integer)
    match_count = Column(Integer)


class MatchDetailView(Base):
    """Materialized view: Match with tournament, participants, and result details."""

    __tablename__ = "projections_matchdetailview"

    match_id = Column(UUID, primary_key=True)
    location = Column(String(255))
    status = Column(String(255))
    start_time = Column(DateTime)

    tournament_id = Column(UUID)
    tournament_name = Column(String(255))

    modality_id = Column(UUID)
    modality_name = Column(String(255))

    participants = Column(JSON)  # List of participants with details
    results = Column(JSON)  # Match results details

    participant_count = Column(Integer)
    comment_count = Column(Integer)

    nucleos_ids = Column(
        ARRAY(UUID), default=list
    )  # List of nucleo IDs involved in the match
    courses_ids = Column(
        ARRAY(UUID), default=list
    )  # List of course IDs involved in the match


class TournamentStandingsView(Base):
    """Materialized view: Tournament standings/rankings."""

    __tablename__ = "projections_tournamentstandingsview"

    tournament_id = Column(UUID, primary_key=True)
    competitor_id = Column(UUID, primary_key=True)
    competitor_type = Column(String(255))
    competitor_entity_id = Column(UUID)
    competitor_name = Column(String(255))
    position = Column(Integer)

    statistics_metadata = Column(JSON, nullable=True)


class GeneralRankingView(Base):
    """Materialized view: General ranking across all courses."""

    __tablename__ = "projections_generalrankingview"

    id = Column(Integer, primary_key=True, autoincrement=True)

    season_id = Column(Integer)
    course_id = Column(UUID)
    course_name = Column(String(255))
    course_abbreviation = Column(String(255))

    nucleo_id = Column(UUID)
    nucleo_name = Column(String(255))
    nucleo_abbreviation = Column(String(255))

    points = Column(Integer)
    rank = Column(Integer)

    tournaments_participated = Column(Integer)


class ModalityRankingView(Base):
    """Materialized view: Modality-specific ranking for courses."""

    __tablename__ = "projections_modalityrankingview"

    id = Column(Integer, primary_key=True, autoincrement=True)

    season_id = Column(Integer)
    modality_id = Column(UUID)
    modality_name = Column(String(255))

    course_id = Column(UUID)
    course_name = Column(String(255))
    course_abbreviation = Column(String(255))

    nucleo_id = Column(UUID)
    nucleo_name = Column(String(255))
    nucleo_abbreviation = Column(String(255))

    points = Column(Integer)
    rank = Column(Integer)


class NucleoDetailView(Base):
    """Materialized view: Nucleo details with aggregated statistics."""

    __tablename__ = "projections_nucleodetailview"

    nucleo_id = Column(UUID, primary_key=True)
    name = Column(String(255))
    abbreviation = Column(String(255))
    logo_url = Column(String(255))


class SeasonDetailView(Base):
    """Materialized view: Season details with aggregated statistics."""

    __tablename__ = "projections_seasondetailview"

    season_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    is_active = Column(Boolean)


class RegulationDetailView(Base):
    """Materialized view: Regulation details with aggregated statistics."""

    __tablename__ = "projections_regulationdetailview"

    id = Column(UUID, primary_key=True)
    title = Column(String(255))
    description = Column(String)
    file_url = Column(String(255))
    season_id = Column(Integer)


class HomePageConfigView(Base):
    """Materialized view: Home page configuration details."""

    __tablename__ = "projections_homepageconfigview"

    _bucket = Column(Integer, primary_key=True)
    title = Column(String(255))
    subtitle = Column(String(255))
    welcome_message = Column(String(255))
    about_us = Column(String)
    hero_image_url = Column(String(255))
    sponsors = Column(JSON)  # List of sponsors with details


class CourseDetailView(Base):
    """Materialized view: Course details with aggregated statistics."""

    __tablename__ = "projections_coursedetailview"

    course_id = Column(UUID, primary_key=True)
    name = Column(String(255))
    abbreviation = Column(String(255))

    nucleo_id = Column(UUID)
    nucleo_name = Column(String(255))
    nucleo_abbreviation = Column(String(255))
    nucleo_logo_url = Column(String(255))
