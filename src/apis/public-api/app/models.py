"""
SQLAlchemy models for Public API - Read Model.
Schema: public_read

These are projection views updated by the Read Model Updater service.
Public API only reads from these views, never writes.
"""

from taca_models import (
    GeneralRankingView,
    MatchDetailView,
    StudentDetailView,
    TeamDetailView,
    TournamentDetailView,
    TournamentStandingsView,
)

__all__ = [
    "TeamDetailView",
    "StudentDetailView",
    "TournamentDetailView",
    "MatchDetailView",
    "TournamentStandingsView",
    "GeneralRankingView",
]
