"""
TACA Read Models Package

Shared SQLAlchemy models for read-only access to TACA microservices data
and read/write access to public_read schema views.
"""

from .metadata import Base
from .models import (  # Enums; Core Read Models; Materialized Views
    Course,
    GeneralRankingView,
    Match,
    MatchComment,
    MatchDetailView,
    MatchLineup,
    MatchParticipant,
    MatchResult,
    MatchStatus,
    Modality,
    ModalityType,
    Nucleo,
    ParticipantType,
    Regulation,
    Staff,
    Student,
    StudentDetailView,
    Team,
    TeamDetailView,
    TeamPlayer,
    Tournament,
    TournamentCompetitor,
    TournamentDetailView,
    TournamentRanking,
    TournamentStandingsView,
    TournamentStatus,
)

__all__ = [
    "Base",
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
    "Staff",
    "Team",
    "TeamPlayer",
    "Tournament",
    "TournamentCompetitor",
    "TournamentRanking",
    "Match",
    "MatchParticipant",
    "MatchResult",
    "MatchLineup",
    "MatchComment",
    # Materialized Views
    "TeamDetailView",
    "StudentDetailView",
    "TournamentDetailView",
    "MatchDetailView",
    "TournamentStandingsView",
    "GeneralRankingView",
    # Shared Operational Tables
    "Regulation",
]

__version__ = "0.1.0"
