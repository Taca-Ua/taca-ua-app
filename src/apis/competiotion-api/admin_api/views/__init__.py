"""
Views package for admin_api
"""

from .courses import CourseDetailView, CourseListCreateView
from .matches import (
    MatchDetailView,
    MatchListCreateView,
    match_comments,
    match_lineup,
    match_result,
    match_sheet,
)
from .modalities import ModalityDetailView, ModalityListCreateView
from .regulations import RegulationDetailView, RegulationListCreateView
from .seasons import SeasonListCreateView, season_finish, season_start
from .students import StudentListCreateView, student_update
from .teams import TeamDetailView, TeamListCreateView
from .tournaments import (
    TournamentDetailView,
    TournamentListCreateView,
    tournament_finish,
)
from .users import NucleoAdminDetailView, NucleoAdminListCreateView

__all__ = [
    # Users
    "NucleoAdminListCreateView",
    "NucleoAdminDetailView",
    # Courses
    "CourseListCreateView",
    "CourseDetailView",
    # Regulations
    "RegulationListCreateView",
    "RegulationDetailView",
    # Modalities
    "ModalityListCreateView",
    "ModalityDetailView",
    # Tournaments
    "TournamentListCreateView",
    "TournamentDetailView",
    "tournament_finish",
    # Teams
    "TeamListCreateView",
    "TeamDetailView",
    # Students
    "StudentListCreateView",
    "student_update",
    # Matches
    "MatchListCreateView",
    "MatchDetailView",
    "match_result",
    "match_lineup",
    "match_comments",
    "match_sheet",
    # Seasons
    "SeasonListCreateView",
    "season_start",
    "season_finish",
]
