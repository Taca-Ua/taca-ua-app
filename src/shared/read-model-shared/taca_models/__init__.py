"""
TACA Read Models Package

Shared SQLAlchemy models for read-only access to TACA microservices data
and read/write access to public_read schema views.
"""

from .metadata import Base
from .models import GamesView, RankingView, TournamentView

__all__ = [
    "Base",
    "GamesView",
    "RankingView",
    "TournamentView",
]

__version__ = "0.1.0"
