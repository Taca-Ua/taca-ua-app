"""
SQLAlchemy models for Public API - Read Model.
Schema: public_read

These are projection views updated by the Read Model Updater service.
Public API only reads from these views, never writes.
"""

from taca_models import GamesView, RankingView, TournamentView

__all__ = [
    "GamesView",
    "RankingView",
    "TournamentView",
]
