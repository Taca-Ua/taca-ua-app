"""
SQLAlchemy models for Read Model Updater Service.

This service listens to events from other microservices and updates
the read-only views in the public_read schema.

All models are now imported from the shared taca_models package.
"""

import enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Re-export all models from shared package
from taca_models import (  # Materialized Views
    Base,
    GeneralRankingView,
    MatchDetailView,
    ModalityRankingView,
    NucleoDetailView,
    Regulation,
    SeasonDetailView,
    StudentDetailView,
    TeamDetailView,
    TournamentDetailView,
    TournamentStandingsView,
)

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
    logo_url = Column(String, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    courses = relationship(
        "Course",
        primaryjoin="Nucleo.nucleo_id == foreign(Course.nucleo_id)",
        back_populates="nucleo",
    )


class Course(Base):
    """Course linked to a nucleo - populated from modalities service events."""

    __tablename__ = "courses"
    __table_args__ = {"schema": "public_read"}

    course_id = Column(UUID(as_uuid=True), primary_key=True)
    nucleo_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    nucleo = relationship(
        "Nucleo",
        primaryjoin="Course.nucleo_id == Nucleo.nucleo_id",
        foreign_keys=[nucleo_id],
        back_populates="courses",
    )
    students = relationship(
        "Student",
        primaryjoin="Course.course_id == Student.course_id",
        foreign_keys="[Student.course_id]",
        back_populates="course",
    )
    teams = relationship(
        "Team",
        primaryjoin="Course.course_id == Team.course_id",
        foreign_keys="[Team.course_id]",
        back_populates="course",
    )


class ModalityType(Base):
    """Sport type with escaloes configuration - populated from modalities service events."""

    __tablename__ = "modality_types"
    __table_args__ = {"schema": "public_read"}

    modality_type_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    escaloes = Column(JSON, nullable=False)  # Array of escalao definitions
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    modalities = relationship(
        "Modality",
        primaryjoin="ModalityType.modality_type_id == Modality.modality_type_id",
        foreign_keys="[Modality.modality_type_id]",
        back_populates="modality_type",
    )


class Modality(Base):
    """Instance of a modality type - populated from modalities service events."""

    __tablename__ = "modalities"
    __table_args__ = {"schema": "public_read"}

    modality_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_type_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    modality_type = relationship(
        "ModalityType",
        primaryjoin="Modality.modality_type_id == ModalityType.modality_type_id",
        foreign_keys=[modality_type_id],
        back_populates="modalities",
    )
    teams = relationship(
        "Team",
        primaryjoin="Modality.modality_id == Team.modality_id",
        foreign_keys="[Team.modality_id]",
        back_populates="modality",
    )
    tournaments = relationship(
        "Tournament",
        primaryjoin="Modality.modality_id == Tournament.modality_id",
        foreign_keys="[Tournament.modality_id]",
        back_populates="modality",
    )


class Student(Base):
    """Student information - populated from modalities service events."""

    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("student_number", name="uq_student_number"),
        {"schema": "public_read"},
    )

    student_id = Column(UUID(as_uuid=True), primary_key=True)
    course_id = Column(UUID(as_uuid=True), nullable=False)
    student_number = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    is_member = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    course = relationship(
        "Course",
        primaryjoin="Student.course_id == Course.course_id",
        foreign_keys=[course_id],
        back_populates="students",
    )
    team_memberships = relationship(
        "TeamPlayer",
        primaryjoin="Student.student_id == TeamPlayer.student_id",
        foreign_keys="[TeamPlayer.student_id]",
        back_populates="student",
    )


class Team(Base):
    """Team information - populated from modalities service events."""

    __tablename__ = "teams"
    __table_args__ = {"schema": "public_read"}

    team_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    course_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    season_id = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    modality = relationship(
        "Modality",
        primaryjoin="Team.modality_id == Modality.modality_id",
        foreign_keys=[modality_id],
        back_populates="teams",
    )
    course = relationship(
        "Course",
        primaryjoin="Team.course_id == Course.course_id",
        foreign_keys=[course_id],
        back_populates="teams",
    )
    players = relationship(
        "TeamPlayer",
        primaryjoin="Team.team_id == TeamPlayer.team_id",
        foreign_keys="[TeamPlayer.team_id]",
        back_populates="team",
    )
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
    team_id = Column(UUID(as_uuid=True), nullable=False)
    student_id = Column(UUID(as_uuid=True), nullable=False)
    removed_at = Column(DateTime, nullable=True)

    # Relationships
    team = relationship(
        "Team",
        primaryjoin="TeamPlayer.team_id == Team.team_id",
        foreign_keys=[team_id],
        back_populates="players",
    )
    student = relationship(
        "Student",
        primaryjoin="TeamPlayer.student_id == Student.student_id",
        foreign_keys=[student_id],
        back_populates="team_memberships",
    )


class Tournament(Base):
    """Tournament information - populated from tournaments service events."""

    __tablename__ = "tournaments"
    __table_args__ = {"schema": "public_read"}

    tournament_id = Column(UUID(as_uuid=True), primary_key=True)
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    season_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Relationships
    modality = relationship(
        "Modality",
        primaryjoin="Tournament.modality_id == Modality.modality_id",
        foreign_keys=[modality_id],
        back_populates="tournaments",
    )
    competitors = relationship(
        "TournamentCompetitor",
        primaryjoin="Tournament.tournament_id == TournamentCompetitor.tournament_id",
        foreign_keys="[TournamentCompetitor.tournament_id]",
        back_populates="tournament",
    )
    matches = relationship(
        "Match",
        primaryjoin="Tournament.tournament_id == Match.tournament_id",
        foreign_keys="[Match.tournament_id]",
        back_populates="tournament",
    )


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
    tournament_id = Column(UUID(as_uuid=True), nullable=False)
    competitor_type = Column(SQLEnum(ParticipantType), nullable=False)
    competitor_entity_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # team_id or student_id
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    tournament = relationship(
        "Tournament",
        primaryjoin="TournamentCompetitor.tournament_id == Tournament.tournament_id",
        foreign_keys=[tournament_id],
        back_populates="competitors",
    )


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
    tournament_id = Column(UUID(as_uuid=True), nullable=False)
    location = Column(String, nullable=False)
    status = Column(SQLEnum(MatchStatus), nullable=False)
    start_time = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    tournament = relationship(
        "Tournament",
        primaryjoin="Match.tournament_id == Tournament.tournament_id",
        foreign_keys=[tournament_id],
        back_populates="matches",
    )
    participants = relationship(
        "MatchParticipant",
        primaryjoin="Match.match_id == MatchParticipant.match_id",
        foreign_keys="[MatchParticipant.match_id]",
        back_populates="match",
    )
    results = relationship(
        "MatchResult",
        primaryjoin="Match.match_id == MatchResult.match_id",
        foreign_keys="[MatchResult.match_id]",
        back_populates="match",
    )
    comments = relationship(
        "MatchComment",
        primaryjoin="Match.match_id == MatchComment.match_id",
        foreign_keys="[MatchComment.match_id]",
        back_populates="match",
    )


class MatchParticipant(Base):
    """Participant in a match - populated from match.participant events.

    participant_id is now the competitor_id from TournamentCompetitor.
    """

    __tablename__ = "match_participants"
    __table_args__ = (
        Index("ix_match_participants_match_id", "match_id"),
        UniqueConstraint("match_id", "participant_id", name="uq_match_participant"),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(UUID(as_uuid=True), nullable=False)
    participant_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # competitor_id from TournamentCompetitor
    removed_at = Column(DateTime, nullable=True)

    # Relationships
    match = relationship(
        "Match",
        primaryjoin="MatchParticipant.match_id == Match.match_id",
        foreign_keys=[match_id],
        back_populates="participants",
    )
    result = relationship(
        "MatchResult",
        primaryjoin="MatchParticipant.participant_id == MatchResult.participant_id",
        foreign_keys="[MatchResult.participant_id]",
        back_populates="participant",
        uselist=False,
    )


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
    match_id = Column(UUID(as_uuid=True), nullable=False)
    participant_id = Column(UUID(as_uuid=True), nullable=False)
    score = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)
    results_metadata = Column(JSON, nullable=True)

    # Relationships
    match = relationship(
        "Match",
        primaryjoin="MatchResult.match_id == Match.match_id",
        foreign_keys=[match_id],
        back_populates="results",
    )
    participant = relationship(
        "MatchParticipant",
        primaryjoin="MatchResult.participant_id == MatchParticipant.participant_id",
        foreign_keys=[participant_id],
        back_populates="result",
    )


class MatchComment(Base):
    """Comment on a match - populated from match.comment events."""

    __tablename__ = "match_comments"
    __table_args__ = (
        Index("ix_match_comments_match_id", "match_id"),
        {"schema": "public_read"},
    )

    comment_id = Column(UUID(as_uuid=True), primary_key=True)
    match_id = Column(UUID(as_uuid=True), nullable=False)
    message = Column(Text, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    match = relationship(
        "Match",
        primaryjoin="MatchComment.match_id == Match.match_id",
        foreign_keys=[match_id],
        back_populates="comments",
    )


class GeneralRankings(Base):
    """General rankings for courses - populated from ranking.computed events."""

    __tablename__ = "general_rankings"
    __table_args__ = (
        Index("ix_general_rankings_course_id", "course_id"),
        UniqueConstraint(
            "course_id", "season_id", name="uq_general_rankings_course_season"
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, nullable=False)
    course_id = Column(UUID(as_uuid=True), nullable=False)
    points = Column(Integer, nullable=False, default=0)
    tournaments_participated = Column(Integer, nullable=False, default=0)


class ModalityRankings(Base):
    """Rankings for courses within a modality - populated from ranking.computed events."""

    __tablename__ = "modality_rankings"
    __table_args__ = (
        Index("ix_modality_rankings_modality_id", "modality_id"),
        Index("ix_modality_rankings_course_id", "course_id"),
        UniqueConstraint(
            "modality_id",
            "course_id",
            "season_id",
            name="uq_modality_rankings_course_modality_season",
        ),
        {"schema": "public_read"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_id = Column(Integer, nullable=False)
    modality_id = Column(UUID(as_uuid=True), nullable=False)
    course_id = Column(UUID(as_uuid=True), nullable=False)
    points = Column(Integer, nullable=False, default=0)


class Season(Base):
    """Season information - populated from seasons service events."""

    __tablename__ = "seasons"
    __table_args__ = {"schema": "public_read"}

    season_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    finished_at = Column(DateTime, nullable=True)


__all__ = [
    # Enums
    "ParticipantType",
    "MatchStatus",
    "TournamentStatus",
    # Core Read Models
    "Nucleo",
    "Course",
    "ModalityType",
    "Modality",
    "Student",
    "Team",
    "TeamPlayer",
    "Tournament",
    "TournamentCompetitor",
    "Match",
    "MatchParticipant",
    "MatchResult",
    "MatchComment",
    "Regulation",
    # Materialized Views
    "TeamDetailView",
    "StudentDetailView",
    "TournamentDetailView",
    "MatchDetailView",
    "TournamentStandingsView",
    "GeneralRankingView",
    "ModalityRankings",
    "GeneralRankings",
    "ModalityRankingView",
    "NucleoDetailView",
    "SeasonDetailView",
]
