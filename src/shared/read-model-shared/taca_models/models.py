"""
SQLAlchemy models for Read Model tables.

This package contains models for the public_read schema that aggregate
data from multiple microservices via events.

All models are read/write projections maintained by the read-model-updater service.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .metadata import Base


# ==================== ENUMS ====================


class MatchStatus(enum.Enum):
    """Match status enum"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class TournamentStatus(enum.Enum):
    """Tournament status enum"""

    DRAFT = "draft"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class ParticipantType(enum.Enum):
    """Participant type enum"""

    TEAM = "team"
    ATHLETE = "athlete"


# ==================== CORE ENTITIES ====================


class Nucleo(Base):
    """Organizational unit (nucleo) projection"""

    __tablename__ = "nucleos"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    courses = relationship("Course", back_populates="nucleo")


class Course(Base):
    """Course projection"""

    __tablename__ = "courses"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    nucleo_id = Column(UUID(as_uuid=True), ForeignKey("public_read.nucleos.id"))
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    nucleo = relationship("Nucleo", back_populates="courses")
    students = relationship("Student", back_populates="course")
    teams = relationship("Team", back_populates="course")


class ModalityType(Base):
    """Sport/modality type projection"""

    __tablename__ = "modality_types"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    escaloes = Column(JSON, nullable=False)  # List of escalao definitions
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    modalities = relationship("Modality", back_populates="modality_type")


class Modality(Base):
    """Modality projection"""

    __tablename__ = "modalities"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    modality_type_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.modality_types.id")
    )
    name = Column(String(100))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    modality_type = relationship("ModalityType", back_populates="modalities")
    teams = relationship("Team", back_populates="modality")
    tournaments = relationship("Tournament", back_populates="modality")


class Student(Base):
    """Student projection"""

    __tablename__ = "students"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("public_read.courses.id"))
    student_number = Column(String(50), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    is_member = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    course = relationship("Course", back_populates="students")
    team_memberships = relationship("TeamPlayer", back_populates="student")
    match_lineups = relationship("MatchLineup", back_populates="player")


class Staff(Base):
    """Staff projection"""

    __tablename__ = "staff"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    staff_number = Column(String(50), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)


class Team(Base):
    """Team projection"""

    __tablename__ = "teams"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(UUID(as_uuid=True), ForeignKey("public_read.modalities.id"))
    course_id = Column(UUID(as_uuid=True), ForeignKey("public_read.courses.id"))
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    modality = relationship("Modality", back_populates="teams")
    course = relationship("Course", back_populates="teams")
    players = relationship("TeamPlayer", back_populates="team")
    tournament_participations = relationship("TournamentCompetitor", back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.team_home_id")
    away_matches = relationship("Match", foreign_keys="Match.team_away_id")


class TeamPlayer(Base):
    """Team player association projection"""

    __tablename__ = "team_players"
    __table_args__ = {"schema": "public_read"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("public_read.teams.id"))
    student_id = Column(UUID(as_uuid=True), ForeignKey("public_read.students.id"))
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    team = relationship("Team", back_populates="players")
    student = relationship("Student", back_populates="team_memberships")


# ==================== TOURNAMENT ENTITIES ====================


class Tournament(Base):
    """Tournament projection"""

    __tablename__ = "tournaments"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(UUID(as_uuid=True), ForeignKey("public_read.modalities.id"))
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    modality = relationship("Modality", back_populates="tournaments")
    competitors = relationship("TournamentCompetitor", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")


class TournamentCompetitor(Base):
    """Tournament competitor association projection"""

    __tablename__ = "tournament_competitors"
    __table_args__ = {"schema": "public_read"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("public_read.tournaments.id"))
    competitor_type = Column(String(10))  # 'team' or 'athlete'
    competitor_entity_id = Column(UUID(as_uuid=True))  # team_id or student_id
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    tournament = relationship("Tournament", back_populates="competitors")
    team = relationship("Team", back_populates="tournament_participations", 
                       foreign_keys="[TournamentCompetitor.competitor_entity_id]",
                       primaryjoin="and_(TournamentCompetitor.competitor_entity_id==Team.id, TournamentCompetitor.competitor_type=='team')")


# ==================== MATCH ENTITIES ====================


class Match(Base):
    """Match projection"""

    __tablename__ = "matches"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    tournament_id = Column(
        UUID(as_uuid=True), ForeignKey("public_read.tournaments.id"), nullable=True
    )
    location = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    # Denormalized team info for easy querying
    team_home_id = Column(UUID(as_uuid=True))
    team_away_id = Column(UUID(as_uuid=True))
    team_home_name = Column(String(100))
    team_away_name = Column(String(100))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    participants = relationship("MatchParticipant", back_populates="match")
    results = relationship("MatchResult", back_populates="match")
    lineups = relationship("MatchLineup", back_populates="match")
    comments = relationship("MatchComment", back_populates="match")


class MatchParticipant(Base):
    """Match participant projection"""

    __tablename__ = "match_participants"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("public_read.matches.id"))
    participant_type = Column(String(10))  # 'team' or 'athlete'
    participant_entity_id = Column(UUID(as_uuid=True))  # team_id or student_id
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    match = relationship("Match", back_populates="participants")


class MatchResult(Base):
    """Match result projection"""

    __tablename__ = "match_results"
    __table_args__ = {"schema": "public_read"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("public_read.matches.id"))
    participant_id = Column(UUID(as_uuid=True), nullable=False)  # from participant table
    score = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    results_metadata = Column(JSON, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="results")


class MatchLineup(Base):
    """Match lineup projection"""

    __tablename__ = "match_lineups"
    __table_args__ = {"schema": "public_read"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("public_read.matches.id"))
    team_id = Column(UUID(as_uuid=True), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("public_read.students.id"))
    jersey_number = Column(Integer, nullable=False)
    is_starter = Column(Boolean, nullable=False, default=False)
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="lineups")
    player = relationship("Student", back_populates="match_lineups")


class MatchComment(Base):
    """Match comment projection"""

    __tablename__ = "match_comments"
    __table_args__ = {"schema": "public_read"}

    id = Column(UUID(as_uuid=True), primary_key=True)
    match_id = Column(UUID(as_uuid=True), ForeignKey("public_read.matches.id"))
    message = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)  # user who created comment
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    match = relationship("Match", back_populates="comments")


# ==================== VIEW MODELS (Legacy Support) ====================


class GamesView(Base):
    """Enhanced games view with more detail"""

    __tablename__ = "games_view"
    __table_args__ = {"schema": "public_read"}

    game_id = Column(UUID(as_uuid=True), primary_key=True)
    # Tournament info
    tournament_id = Column(UUID(as_uuid=True))
    tournament_name = Column(Text)
    tournament_status = Column(Text)
    # Modality info
    modality_id = Column(UUID(as_uuid=True))
    modality_name = Column(Text)
    modality_type_name = Column(Text)
    # Team info
    team_a_id = Column(UUID(as_uuid=True))
    team_a_name = Column(Text)
    team_a_course = Column(Text)
    team_b_id = Column(UUID(as_uuid=True))
    team_b_name = Column(Text)
    team_b_course = Column(Text)
    # Match details
    location = Column(Text)
    score = Column(Text)  # "X-Y" format or custom
    scheduled_at = Column(DateTime)
    state = Column(Text)
    # Metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class TournamentView(Base):
    """Enhanced tournament view with more detail"""

    __tablename__ = "tournament_view"
    __table_args__ = {"schema": "public_read"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text)
    status = Column(Text)
    start_date = Column(DateTime)
    # Modality info
    modality_id = Column(UUID(as_uuid=True))
    modality_name = Column(Text)
    modality_type_name = Column(Text)
    # Stats
    total_competitors = Column(Integer)
    total_matches = Column(Integer)
    completed_matches = Column(Integer)
    # Metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class RankingView(Base):
    """Enhanced ranking view with team details"""

    __tablename__ = "ranking_view"
    __table_args__ = {"schema": "public_read"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tournament_id = Column(UUID(as_uuid=True), nullable=False)
    team_id = Column(UUID(as_uuid=True), nullable=False)
    team_name = Column(Text, nullable=False)
    course_name = Column(Text)
    course_abbreviation = Column(Text)
    nucleo_name = Column(Text)
    # Ranking data
    points = Column(Integer, default=0)
    position = Column(Integer)
    matches_played = Column(Integer, default=0)
    matches_won = Column(Integer, default=0)
    matches_lost = Column(Integer, default=0)
    matches_drawn = Column(Integer, default=0)
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow)
