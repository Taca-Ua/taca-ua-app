"""
Routes package for public API
"""

from .calendar import router as calendar_router
from .courses import router as courses_router
from .history import router as history_router
from .modalities import router as modalities_router
from .rankings import router as rankings_router
from .regulations import router as regulations_router
from .results import router as results_router
from .seasons import router as seasons_router
from .teams import router as teams_router
from .tournaments import router as tournaments_router

# Collect all routers for registration in main.py
all_routers = [
    calendar_router,
    results_router,
    rankings_router,
    tournaments_router,
    modalities_router,
    courses_router,
    regulations_router,
    history_router,
    seasons_router,
    teams_router,
]

__all__ = [
    "calendar_router",
    "results_router",
    "rankings_router",
    "tournaments_router",
    "modalities_router",
    "courses_router",
    "regulations_router",
    "history_router",
    "seasons_router",
    "teams_router",
    "all_routers",
]
