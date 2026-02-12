"""
TACA Read Models Package

Shared SQLAlchemy models for read-only access to TACA microservices data
and read/write access to public_read schema views.
"""

from .metadata import Base
from .models import (
    # Core entities
    Course,
    Modality,
    ModalityType,
    Nucleo,
    Staff,
    Student,
    Team,
    TeamPlayer,
    # Tournament entities
    Tournament,
    TournamentCompetitor,
    # Match entities
    Match,
    MatchComment,
    MatchLineup,
    MatchParticipant,
    MatchResult,
    # View models (legacy)
    GamesView,
    RankingView,
    TournamentView,
    # Enums
    MatchStatus,
    ParticipantType,
    TournamentStatus,
)

__all__ = [
    "Base",
    # Core entities
    "Nucleo",
    "Course",
    "ModalityType",
    "Modality",
    "Student",
    "Staff",
    "Team",
    "TeamPlayer",
    # Tournament entities
    "Tournament",
    "TournamentCompetitor",
    # Match entities
    "Match",
    "MatchParticipant",
    "MatchResult",
    "MatchLineup",
    "MatchComment",
    # View models (legacy)
    "GamesView",
    "TournamentView",
    "RankingView",
    # Enums
    "MatchStatus",
    "TournamentStatus",
    "ParticipantType",
]

__version__ = "0.1.0"
