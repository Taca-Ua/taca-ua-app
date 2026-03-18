"""
SQLAlchemy models for Read Model Updater Service.

This service listens to events from other microservices and updates
the read-only views in the public_read schema.

All models are now imported from the shared taca_models package.
"""

# Re-export all models from shared package
from taca_models import (  # Enums; Core Read Models; Materialized Views
    Course,
    GeneralRankings,
    GeneralRankingView,
    Match,
    MatchComment,
    MatchDetailView,
    MatchLineup,
    MatchParticipant,
    MatchResult,
    MatchStatus,
    Modality,
    ModalityRankings,
    ModalityType,
    Nucleo,
    ParticipantType,
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
    "ModalityRankings",
    "GeneralRankings",
]
