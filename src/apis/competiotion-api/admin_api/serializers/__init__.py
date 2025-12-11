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
from .modality_types import (
    ModalityTypeCreateSerializer,
    ModalityTypeDetailSerializer,
    ModalityTypeListSerializer,
    ModalityTypeUpdateSerializer,
)
from .nucleus import (
    NucleosCreateSerializer,
    NucleosListSerializer,
    NucleosUpdateSerializer,
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
    # Modality Types
    "ModalityTypeListSerializer",
    "ModalityTypeCreateSerializer",
    "ModalityTypeUpdateSerializer",
    "ModalityTypeDetailSerializer",
    # Nucleus
    "NucleosListSerializer",
    "NucleosCreateSerializer",
    "NucleosUpdateSerializer",
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
