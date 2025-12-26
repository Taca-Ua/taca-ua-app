"""
SQLAlchemy models for Read Model Updater Service.

This service listens to events from other microservices and updates
the read-only views in the public_read schema.

All models are now imported from the shared taca_models package.
"""

# Re-export models from shared package for backwards compatibility
from taca_models import GamesView, RankingView, TournamentView

__all__ = [
    "GamesView",
    "RankingView",
    "TournamentView",
]
