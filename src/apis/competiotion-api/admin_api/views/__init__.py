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
from .modalities_types import ModalityTypeDetailView, ModalityTypeListCreateView
from .nucleus import NucleoDetailView, NucleoListCreateView
from .public import calendar, modality_list
from .regulations import RegulationDetailView, RegulationListCreateView
from .seasons import SeasonListCreateView, season_finish, season_start
from .staff import StaffDetailView, StaffListCreateView
from .students import StudentDetailView, StudentListCreateView
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
    # Modality Types
    "ModalityTypeListCreateView",
    "ModalityTypeDetailView",
    # Modalities
    "ModalityListCreateView",
    "ModalityDetailView",
    # Nucleos
    "NucleoListCreateView",
    "NucleoDetailView",
    # Tournaments
    "TournamentListCreateView",
    "TournamentDetailView",
    "tournament_finish",
    # Teams
    "TeamListCreateView",
    "TeamDetailView",
    # Students
    "StudentListCreateView",
    "StudentDetailView",
    # Staff
    "StaffListCreateView",
    "StaffDetailView",
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
    # Public API
    "calendar",
    "modality_list",
]
