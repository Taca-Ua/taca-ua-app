"""
SQLAlchemy models for Read Model Updater Service.

This service listens to events from other microservices and updates
the read-only views in the public_read schema.

All models are now imported from the shared taca_models package.
"""

# Re-export all models from shared package
from taca_models import (
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
    # View models (enhanced for public API)
    GamesView,
    RankingView,
    TournamentView,
    # Enums for validation
    MatchStatus,
    ParticipantType,
    TournamentStatus,
)

__all__ = [
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
    # View models for public API
    "GamesView",
    "TournamentView",
    "RankingView",
    # Enums
    "MatchStatus",
    "TournamentStatus",
    "ParticipantType",
]
