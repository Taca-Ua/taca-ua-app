"""
Views package for admin_api
"""

from .auth import login, logout, me
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
from .students import StudentListCreateView, student_detail
from .teams import TeamDetailView, TeamListCreateView
from .tournaments import (
    TournamentDetailView,
    TournamentListCreateView,
    tournament_finish,
)
from .users import (
    AdministratorDetailView,
    AdministratorListCreateView,
    NucleoAdminDetailView,
    NucleoAdminListCreateView,
)

__all__ = [
    # Authentication
    "login",
    "logout",
    "me",
    # Administrators
    "AdministratorListCreateView",
    "AdministratorDetailView",
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
    "student_detail",
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
