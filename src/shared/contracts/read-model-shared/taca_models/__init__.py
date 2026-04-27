"""
TACA Read Models Package

Shared SQLAlchemy models for read-only access to TACA microservices data
and read/write access to public_read schema views.
"""

from .metadata import Base
from .models import (  # Enums; Core Read Models; Materialized Views
    HEAD,
    GeneralRankingView,
    MatchDetailView,
    ModalityRankingView,
    Regulation,
    Season,
    Staff,
    Student,
    StudentDetailView,
    TeamDetailView,
    TournamentDetailView,
    TournamentStandingsView,
    02edffb2045a79c2f37d752e668240a5161cf0dd,
    <<<<<<<,
    =======,
    >>>>>>>,
)

__all__ = [
    "Base",
<<<<<<< HEAD
=======
    # Enums
    "ParticipantType",
    "MatchStatus",
    "TournamentStatus",
    # Core Read Models
    "Season",
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
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd
    # Materialized Views
    "TeamDetailView",
    "StudentDetailView",
    "TournamentDetailView",
    "MatchDetailView",
    "TournamentStandingsView",
    "GeneralRankingView",
    # Shared Operational Tables
    "Regulation",
    "GeneralRankings",
    "ModalityRankings",
    "ModalityRankingView",
]

__version__ = "0.1.0"
