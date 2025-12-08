"""
Serializers package for admin_api
"""

from .auth import LoginRequestSerializer, LoginResponseSerializer, UserInfoSerializer
from .courses import (
    CourseCreateSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)
from .matches import (
    MatchCommentSerializer,
    MatchCreateSerializer,
    MatchLineupSerializer,
    MatchListSerializer,
    MatchResultSerializer,
    MatchUpdateSerializer,
)
from .modalities import (
    ModalityCreateSerializer,
    ModalityListSerializer,
    ModalityUpdateSerializer,
)
from .regulations import (
    RegulationCreateSerializer,
    RegulationListSerializer,
    RegulationUpdateSerializer,
)
from .seasons import SeasonCreateSerializer, SeasonListSerializer
from .students import (
    StudentCreateSerializer,
    StudentListSerializer,
    StudentUpdateSerializer,
)
from .teams import TeamCreateSerializer, TeamListSerializer, TeamUpdateSerializer
from .tournaments import (
    TournamentCreateSerializer,
    TournamentListSerializer,
    TournamentUpdateSerializer,
)
from .users import (
    NucleoAdminCreateSerializer,
    NucleoAdminListSerializer,
    NucleoAdminUpdateSerializer,
)

__all__ = [
    # Authentication
    "LoginRequestSerializer",
    "LoginResponseSerializer",
    "UserInfoSerializer",
    # Users
    "NucleoAdminListSerializer",
    "NucleoAdminCreateSerializer",
    "NucleoAdminUpdateSerializer",
    # Courses
    "CourseListSerializer",
    "CourseCreateSerializer",
    "CourseUpdateSerializer",
    # Regulations
    "RegulationListSerializer",
    "RegulationCreateSerializer",
    "RegulationUpdateSerializer",
    # Modalities
    "ModalityListSerializer",
    "ModalityCreateSerializer",
    "ModalityUpdateSerializer",
    # Tournaments
    "TournamentListSerializer",
    "TournamentCreateSerializer",
    "TournamentUpdateSerializer",
    # Teams
    "TeamListSerializer",
    "TeamCreateSerializer",
    "TeamUpdateSerializer",
    # Students
    "StudentListSerializer",
    "StudentCreateSerializer",
    "StudentUpdateSerializer",
    # Matches
    "MatchListSerializer",
    "MatchCreateSerializer",
    "MatchUpdateSerializer",
    "MatchResultSerializer",
    "MatchLineupSerializer",
    "MatchCommentSerializer",
    # Seasons
    "SeasonListSerializer",
    "SeasonCreateSerializer",
]
