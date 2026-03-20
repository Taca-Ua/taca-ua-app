"""
SQLAlchemy models for Read Model tables.

This package contains models for the public_read schema that aggregate
data from multiple microservices via events.

All models are read/write projections maintained by the read-model-updater service.
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, Date, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .metadata import Base

# ==================== Enums ====================


class ParticipantType(str, enum.Enum):
    """Type of participant in matches/tournaments."""

    TEAM = "team"
    ATHLETE = "athlete"


class MatchStatus(str, enum.Enum):
    """Status of a match."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class TournamentStatus(str, enum.Enum):
    """Status of a tournament."""

    DRAFT = "draft"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"


# ==================== Core Read Models ====================


class Nucleo(Base):
    """Organizational unit (nucleo) - populated from modalities service events."""

    __tablename__ = "nucleos"
    __table_args__ = {"schema": "public_read"}

    nucleo_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    courses = relationship("Course", back_populates="nucleo")


class Course(Base):
    """Course linked to a nucleo - populated from modalities service events."""

    __tablename__ = "courses"
    __table_args__ = {"schema": "public_read"}

    course_id = Column(UUID(as_uuid=True), primary_key=True)
    nucleo_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.nucleos.nucleo_id"), nullable=False
    )
    name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    nucleo = relationship("Nucleo", back_populates="courses")
    students = relationship("Student", back_populates="course")
    teams = relationship("Team", back_populates="course")


class ModalityType(Base):
    """Sport type with escaloes configuration - populated from modalities service events."""

    __tablename__ = "modality_types"
    __table_args__ = {"schema": "public_read"}

    modality_type_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    escaloes = Column(JSON, nullable=False)  # Array of escalao definitions

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    modalities = relationship("Modality", back_populates="modality_type")


class Modality(Base):
    """Instance of a modality type - populated from modalities service events."""

    __tablename__ = "modalities"
    __table_args__ = {"schema": "public_read"}

    modality_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.modality_types.modality_type_id"),
        nullable=False,
    )
    name = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    modality_type = relationship("ModalityType", back_populates="modalities")
    teams = relationship("Team", back_populates="modality")
    tournaments = relationship("Tournament", back_populates="modality")


class Student(Base):
    """Student information - populated from modalities service events."""

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("student_number", name="uq_student_number"),
        {"schema": "public_read"},
    )

    student_id = Column(UUID(as_uuid=True), primary_key=True)
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.courses.course_id"), nullable=False
    )
    student_number = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    is_member = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    course = relationship("Course", back_populates="students")
    team_memberships = relationship("TeamPlayer", back_populates="student")


class Staff(Base):
    """Staff member information - populated from modalities service events."""

    __tablename__ = "staff"
    __table_args__ = (
        UniqueConstraint("staff_number", name="uq_staff_number"),
        {"schema": "public_read"},
    )

    staff_id = Column(UUID(as_uuid=True), primary_key=True)
    full_name = Column(String, nullable=False)
    staff_number = Column(String, nullable=False, unique=True)
    contact = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)


class Team(Base):
    """Team information - populated from modalities service events."""

    __tablename__ = "teams"
    __table_args__ = {"schema": "public_read"}

    team_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.modalities.modality_id"),
        nullable=False,
    )
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.courses.course_id"), nullable=False
    )
    name = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    modality = relationship("Modality", back_populates="teams")
    course = relationship("Course", back_populates="teams")
    players = relationship("TeamPlayer", back_populates="team")
    tournament_entries = relationship(
        "TournamentCompetitor",
        foreign_keys="[TournamentCompetitor.competitor_entity_id]",
        primaryjoin="and_(Team.team_id==foreign(TournamentCompetitor.competitor_entity_id), TournamentCompetitor.competitor_type=='team')",
        viewonly=True,
    )


class TeamPlayer(Base):
    """Team-Student association - populated from team.player_added/removed events."""

    __tablename__ = "team_players"
    __table_args__ = (
        Index("ix_team_players_team_id", "team_id"),
        Index("ix_team_players_student_id", "student_id"),
        UniqueConstraint("team_id", "student_id", name="uq_team_student"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.teams.team_id"), nullable=False
    )
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.students.student_id"),
        nullable=False,
    )

    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)

    # Relationships
    team = relationship("Team", back_populates="players")
    student = relationship("Student", back_populates="team_memberships")


class Tournament(Base):
    """Tournament information - populated from tournaments service events."""

    __tablename__ = "tournaments"
    __table_args__ = {"schema": "public_read"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.modalities.modality_id"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Relationships
    modality = relationship("Modality", back_populates="tournaments")
    competitors = relationship("TournamentCompetitor", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")


class TournamentCompetitor(Base):
    """Competitor in a tournament - populated from tournament.competitor events."""

    __tablename__ = "tournament_competitors"
    __table_args__ = (
        Index("ix_tournament_competitors_tournament_id", "tournament_id"),
        Index("ix_tournament_competitors_entity_id", "competitor_entity_id"),
        UniqueConstraint(
            "tournament_id", "competitor_entity_id", name="uq_tournament_competitor"
        ),
        {"schema": "public_read"},
    )

    competitor_id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.tournaments.tournament_id"),
        nullable=False,
    )
    competitor_type = Column(SQLEnum(ParticipantType), nullable=False)
    competitor_entity_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # team_id or student_id

    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    tournament = relationship("Tournament", back_populates="competitors")


class TournamentRanking(Base):
    """Final ranking entries for a finished tournament - populated from tournament.finished event."""

    __tablename__ = "tournament_rankings"
    __table_args__ = (
        Index("ix_tournament_rankings_tournament_id", "tournament_id"),
        Index("ix_tournament_rankings_position", "tournament_id", "position"),
        UniqueConstraint(
            "tournament_id", "competitor_id", name="uq_tournament_ranking"
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.tournaments.tournament_id"),
        nullable=False,
    )
    competitor_id = Column(UUID(as_uuid=True), nullable=False)
    position = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    tournament = relationship("Tournament", foreign_keys=[tournament_id])


class Match(Base):
    """Match information - populated from matches service events."""

    __tablename__ = "matches"
    __table_args__ = (
        Index("ix_matches_tournament_id", "tournament_id"),
        Index("ix_matches_status", "status"),
        Index("ix_matches_start_time", "start_time"),
        {"schema": "public_read"},
    )

    match_id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.tournaments.tournament_id"),
        nullable=False,
    )
    location = Column(String, nullable=False)
    status = Column(SQLEnum(MatchStatus), nullable=False)
    start_time = Column(DateTime, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    participants = relationship("MatchParticipant", back_populates="match")
    results = relationship("MatchResult", back_populates="match")
    lineups = relationship("MatchLineup", back_populates="match")
    comments = relationship("MatchComment", back_populates="match")


class MatchParticipant(Base):
    """Participant in a match - populated from match.participant events."""

    __tablename__ = "match_participants"
    __table_args__ = (
        Index("ix_match_participants_match_id", "match_id"),
        Index("ix_match_participants_entity_id", "participant_entity_id"),
        UniqueConstraint("match_id", "participant_id", name="uq_match_participant"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.matches.match_id"), nullable=False
    )
    participant_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    participant_type = Column(SQLEnum(ParticipantType), nullable=False)
    participant_entity_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # team_id or student_id

    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)

    # Relationships
    match = relationship("Match", back_populates="participants")
    result = relationship("MatchResult", back_populates="participant", uselist=False)


class MatchResult(Base):
    """Result for a match participant - populated from match.result.updated events."""

    __tablename__ = "match_results"
    __table_args__ = (
        Index("ix_match_results_match_id", "match_id"),
        Index("ix_match_results_participant_id", "participant_id"),
        UniqueConstraint("match_id", "participant_id", name="uq_match_result"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.matches.match_id"), nullable=False
    )
    participant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.match_participants.participant_id"),
        nullable=False,
    )
    score = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    results_metadata = Column(JSON, nullable=True)

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    match = relationship("Match", back_populates="results")
    participant = relationship("MatchParticipant", back_populates="result")


class MatchLineup(Base):
    """Lineup for a team in a match - populated from match.lineup.assigned events."""

    __tablename__ = "match_lineups"
    __table_args__ = (
        Index("ix_match_lineups_match_id", "match_id"),
        Index("ix_match_lineups_team_id", "team_id"),
        UniqueConstraint("match_id", "team_id", "player_id", name="uq_match_lineup"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.matches.match_id"), nullable=False
    )
    team_id = Column(UUID(as_uuid=True), nullable=False)
    player_id = Column(UUID(as_uuid=True), nullable=False)
    jersey_number = Column(Integer, nullable=False)
    is_starter = Column(Boolean, nullable=False, default=True)

    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="lineups")


class MatchComment(Base):
    """Comment on a match - populated from match.comment events."""

    __tablename__ = "match_comments"
    __table_args__ = (
        Index("ix_match_comments_match_id", "match_id"),
        {"schema": "public_read"},
    )

    comment_id = Column(UUID(as_uuid=True), primary_key=True)
    match_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.matches.match_id"), nullable=False
    )
    message = Column(Text, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    match = relationship("Match", back_populates="comments")


class GeneralRankings(Base):
    """General rankings for courses - populated from ranking.computed events."""

    __tablename__ = "general_rankings"
    __table_args__ = (
        Index("ix_general_rankings_course_id", "course_id"),
        UniqueConstraint("course_id", name="uq_general_rankings_course"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.courses.course_id"), nullable=False
    )
    points = Column(Integer, nullable=False, default=0)
    tournaments_participated = Column(Integer, nullable=False, default=0)


class ModalityRankings(Base):
    """Rankings for courses within a modality - populated from ranking.computed events."""

    __tablename__ = "modality_rankings"
    __table_args__ = (
        Index("ix_modality_rankings_modality_id", "modality_id"),
        Index("ix_modality_rankings_course_id", "course_id"),
        UniqueConstraint(
            "modality_id", "course_id", name="uq_modality_rankings_modality_course"
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    modality_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public_read.modalities.modality_id"),
        nullable=False,
    )
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.courses.course_id"), nullable=False
    )
    points = Column(Integer, nullable=False, default=0)


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

    # Course info
    course_id = Column(UUID(as_uuid=True), nullable=False)
    course_name = Column(String, nullable=False)
    course_abbreviation = Column(String, nullable=False)

    # Nucleo info
    nucleo_id = Column(UUID(as_uuid=True), nullable=False)
    nucleo_name = Column(String, nullable=False)
    nucleo_abbreviation = Column(String, nullable=False)

    # Modality info
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    modality_name = Column(String, nullable=True)
    modality_type_id = Column(UUID(as_uuid=True), nullable=False)
    modality_type_name = Column(String, nullable=False)

    # Player count
    player_count = Column(Integer, nullable=False, default=0)

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


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

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


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

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


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

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


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

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


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
        UniqueConstraint("course_id", name="uq_general_ranking_course"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
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

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


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
            "modality_id", "course_id", name="uq_modality_ranking_modality_course"
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
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

    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# ==================== Shared Operational Tables ====================


class Regulation(Base):
    """
    Regulation document - read-only reference to the regulation table
    owned by the modalities-service (default public schema).
    """

    __tablename__ = "regulation"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
