"""
SQLAlchemy models for Read Model tables.

This package contains models for the public_read schema that aggregate
data from multiple microservices via events.

All models are read/write projections maintained by the read-model-updater service.
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from .metadata import Base

# ==================== Materialized Views ====================
# These are reconstructed via joins from core read models


class TeamDetailView(Base):
    """
    Materialized view: Team with course, nucleo, and modality details.
    Rebuilt when Team, Course, Nucleo, or Modality events are processed.
    """

    __tablename__ = "mv_team_details"
    __table_args__ = (
        Index("ix_mv_team_details_course_id", "course_id"),
        Index("ix_mv_team_details_modality_id", "modality_id"),
        {"schema": "public_read"},
    )

    team_id = Column(UUID(as_uuid=True), primary_key=True)
    team_name = Column(String, nullable=False)
    team_season_id = Column(Integer, nullable=False)

    # Course info
    course_id = Column(UUID(as_uuid=True), nullable=False)
    course_name = Column(String, nullable=False)
    course_abbreviation = Column(String, nullable=False)

    # Nucleo info
    nucleo_id = Column(UUID(as_uuid=True), nullable=False)
    nucleo_name = Column(String, nullable=False)
    nucleo_abbreviation = Column(String, nullable=False)
    nucleo_logo_url = Column(String(500), nullable=True)

    # Modality info
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    modality_name = Column(String, nullable=True)
    modality_type_id = Column(UUID(as_uuid=True), nullable=False)
    modality_type_name = Column(String, nullable=False)

    # Player count
    player_count = Column(Integer, nullable=False, default=0)
    players = Column(JSON, nullable=False, default=list)  # Array of player details


class StudentDetailView(Base):
    """
    Materialized view: Student with course and nucleo details.
    Rebuilt when Student, Course, or Nucleo events are processed.
    """

    __tablename__ = "mv_student_details"
    __table_args__ = (
        Index("ix_mv_student_details_course_id", "course_id"),
        Index("ix_mv_student_details_student_number", "student_number"),
        {"schema": "public_read"},
    )

    student_id = Column(UUID(as_uuid=True), primary_key=True)
    student_number = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_member = Column(Boolean, nullable=False, default=False)

    # Course info
    course_id = Column(UUID(as_uuid=True), nullable=False)
    course_name = Column(String, nullable=False)
    course_abbreviation = Column(String, nullable=False)

    # Nucleo info
    nucleo_id = Column(UUID(as_uuid=True), nullable=False)
    nucleo_name = Column(String, nullable=False)
    nucleo_abbreviation = Column(String, nullable=False)

    # Team count
    team_count = Column(Integer, nullable=False, default=0)


class TournamentDetailView(Base):
    """
    Materialized view: Tournament with modality and competitor details.
    Rebuilt when Tournament, Modality, or TournamentCompetitor events are processed.
    """

    __tablename__ = "mv_tournament_details"
    __table_args__ = (
        Index("ix_mv_tournament_details_modality_id", "modality_id"),
        Index("ix_mv_tournament_details_status", "status"),
        Index("ix_mv_tournament_details_start_date", "start_date"),
        {"schema": "public_read"},
    )

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_name = Column(String, nullable=False)
    tournament_season_id = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)

    # Modality info
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    modality_name = Column(String, nullable=True)
    modality_type_id = Column(UUID(as_uuid=True), nullable=False)
    modality_type_name = Column(String, nullable=False)

    # Statistics
    competitor_count = Column(Integer, nullable=False, default=0)
    match_count = Column(Integer, nullable=False, default=0)


class MatchDetailView(Base):
    """
    Materialized view: Match with tournament, participants, and result details.
    Rebuilt when Match, Tournament, MatchParticipant, or MatchResult events are processed.
    """

    __tablename__ = "mv_match_details"
    __table_args__ = (
        Index("ix_mv_match_details_tournament_id", "tournament_id"),
        Index("ix_mv_match_details_status", "status"),
        Index("ix_mv_match_details_start_time", "start_time"),
        {"schema": "public_read"},
    )

    match_id = Column(UUID(as_uuid=True), primary_key=True)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)

    # Tournament info
    tournament_id = Column(UUID(as_uuid=True), nullable=False)
    tournament_name = Column(String, nullable=False)

    # Modality info
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    modality_name = Column(String, nullable=True)

    # Participants and results (stored as JSON for flexibility)
    participants = Column(
        JSON, nullable=False, default=list
    )  # Array of participant details
    results = Column(JSON, nullable=True)  # Array of results with scores/positions

    # Statistics
    participant_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)


class TournamentStandingsView(Base):
    """
    Materialized view: Tournament standings/rankings.
    Rebuilt when MatchResult or TournamentCompetitor events are processed.
    """

    __tablename__ = "mv_tournament_standings"
    __table_args__ = (
        Index("ix_mv_tournament_standings_tournament_id", "tournament_id"),
        Index("ix_mv_tournament_standings_rank", "tournament_id", "rank"),
        UniqueConstraint(
            "tournament_id", "competitor_entity_id", name="uq_tournament_standings"
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(UUID(as_uuid=True), nullable=False)
    competitor_type = Column(String, nullable=False)
    competitor_entity_id = Column(UUID(as_uuid=True), nullable=False)
    competitor_name = Column(String, nullable=False)

    # Statistics
    matches_played = Column(Integer, nullable=False, default=0)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    draws = Column(Integer, nullable=False, default=0)
    points = Column(Integer, nullable=False, default=0)
    total_score = Column(Integer, nullable=False, default=0)
    rank = Column(Integer, nullable=True)

    # Additional metadata
    statistics_metadata = Column(JSON, nullable=True)


class GeneralRankingView(Base):
    """
    Materialized view: General ranking across all courses.

    Calculates points earned by each course based on tournament final rankings.
    Points are determined by the modality_type's escaloes configuration, which
    defines point awards based on position and participant count.

    Rebuilt when TournamentRanking entries are created/updated.
    """

    __tablename__ = "mv_general_ranking"
    __table_args__ = (
        Index("ix_mv_general_ranking_rank", "rank"),
        Index("ix_mv_general_ranking_course_id", "course_id"),
        UniqueConstraint(
            "course_id", "season_id", name="uq_mv_general_ranking_course_season"
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, nullable=False)
    course_id = Column(UUID(as_uuid=True), nullable=False)
    course_name = Column(String, nullable=False)
    course_abbreviation = Column(String, nullable=False)

    # Nucleo information
    nucleo_id = Column(UUID(as_uuid=True), nullable=False)
    nucleo_name = Column(String, nullable=False)
    nucleo_abbreviation = Column(String, nullable=False)

    # Rankings
    points = Column(Integer, nullable=False, default=0)
    rank = Column(Integer, nullable=True)

    # Metadata
    tournaments_participated = Column(Integer, nullable=False, default=0)


class ModalityRankingView(Base):
    """
    Materialized view: Modality-specific ranking for courses.

    Similar to GeneralRankingView but calculated separately for each modality.
    Rebuilt when TournamentRanking entries are created/updated for tournaments of that modality.
    """

    __tablename__ = "mv_modality_rankings"
    __table_args__ = (
        Index("ix_mv_modality_rankings_rank", "modality_id", "rank"),
        Index("ix_mv_modality_rankings_course_id", "modality_id", "course_id"),
        UniqueConstraint(
            "modality_id",
            "course_id",
            "season_id",
            name="uq_mv_modality_ranking_modality_course_season",
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, nullable=False)
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    modality_name = Column(String, nullable=True)

    course_id = Column(UUID(as_uuid=True), nullable=False)
    course_name = Column(String, nullable=False)
    course_abbreviation = Column(String, nullable=False)

    # Nucleo information
    nucleo_id = Column(UUID(as_uuid=True), nullable=False)
    nucleo_name = Column(String, nullable=False)
    nucleo_abbreviation = Column(String, nullable=False)

    # Rankings
    points = Column(Integer, nullable=False, default=0)
    rank = Column(Integer, nullable=True)


class NucleoDetailView(Base):
    """
    Materialized view: Nucleo details with aggregated statistics.
    Rebuilt when Nucleo, Course, Student, or Team events are processed.
    """

    __tablename__ = "mv_nucleo_details"
    __table_args__ = (
        Index("ix_mv_nucleo_details_nucleo_id", "id"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    nucleo_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=False)
    logo_url = Column(String(500), nullable=True)


class SeasonDetailView(Base):
    """
    Materialized view: Season details with aggregated statistics.
    Rebuilt when Season events are processed.
    """

    __tablename__ = "mv_season_details"
    __table_args__ = (
        Index("ix_mv_season_details_season_id", "season_id"),
        {"schema": "public_read"},
    )

    season_id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)


# ==================== Shared Operational Tables ====================


class Regulation(Base):
    """
    Regulation document - read-only reference to the regulation table
    owned by the modalities-service (default public schema).
    """

    __tablename__ = "regulation"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=False)
    season_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
