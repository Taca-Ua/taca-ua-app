"""
TACA Read Models Package

Shared SQLAlchemy models for read-only access to TACA microservices data
and read/write access to public_read schema views.
"""

from .metadata import Base
from .models import (  # Enums; Core Read Models; Materialized Views
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

__all__ = [
    "Base",
    # Materialized Views
    "TeamDetailView",
    "StudentDetailView",
    "TournamentDetailView",
    "MatchDetailView",
    "TournamentStandingsView",
    "GeneralRankingView",
    "NucleoDetailView",
    "SeasonDetailView",
    # Shared Operational Tables
    "Regulation",
    "GeneralRankings",
    "ModalityRankings",
    "ModalityRankingView",
]

__version__ = "0.1.0"
