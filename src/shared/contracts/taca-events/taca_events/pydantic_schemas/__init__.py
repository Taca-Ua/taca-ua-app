"""
Pydantic typed event schemas for the TACA system.

Import individual schemas or use ``EventRegistry`` to look up schemas
by routing key.

    from taca_events.pydantic_schemas import (
        EventRegistry,
        MatchCreatedV1, MatchCreatedData,
        TournamentCreatedV1, TournamentCreatedData,
        ...
    )
"""

from .base import EventSchema
from .courses import CourseCreatedV1, CourseDeletedV1, CourseUpdatedV1
from .matches import (  # Data models; Schema classes
    MatchCommentAddedV1,
    MatchCommentDeletedV1,
    MatchCreatedV1,
    MatchDeletedV1,
    MatchLineupAssignedV1,
    MatchParticipantAddedV1,
    MatchParticipantRemovedV1,
    MatchResultUpdatedV1,
    MatchUpdatedV1,
)
from .modalities import (  # Nucleo; Course; ModalityType; Modality; Student; Staff; Team
    ModalityCreatedV1,
    ModalityDeletedV1,
    ModalityUpdatedV1,
)
from .modality_types import (
    ModalityTypeCreatedV1,
    ModalityTypeDeletedV1,
    ModalityTypeUpdatedV1,
)
from .nucleos import NucleoCreatedV1, NucleoDeletedV1, NucleoUpdatedV1
from .ranking import RankingComputedV1
from .registry import EventRegistry
from .regulations import RegulationCreatedV1, RegulationDeletedV1, RegulationUpdatedV1
from .seasons import SeasonCreatedV1
from .staff import StaffCreatedV1, StaffDeletedV1, StaffUpdatedV1
from .students import StudentCreatedV1, StudentDeletedV1, StudentUpdatedV1
from .teams import (
    TeamCreatedV1,
    TeamDeletedV1,
    TeamPlayerAddedV1,
    TeamPlayerRemovedV1,
    TeamUpdatedV1,
)
from .tournaments import (
    TournamentCompetitorAddedV1,
    TournamentCompetitorDeletedV1,
    TournamentCreatedV1,
    TournamentDeletedV1,
    TournamentFinishedV1,
    TournamentLeagueStandingsUpdatedV1,
    TournamentUpdatedV1,
)

__all__ = [
    # Base
    "EventSchema",
    "EventRegistry",
    # Match data
    "MatchCreatedData",
    "MatchUpdatedData",
    "MatchDeletedData",
    "MatchParticipantAddedData",
    "MatchParticipantRemovedData",
    "MatchLineupAssignedData",
    "MatchCommentAddedData",
    "MatchCommentDeletedData",
    "MatchResultUpdatedData",
    "MatchParticipantData",
    "LineupPlayerData",
    "MatchResultEntryData",
    # Match schemas
    "MatchCreatedV1",
    "MatchUpdatedV1",
    "MatchDeletedV1",
    "MatchParticipantAddedV1",
    "MatchParticipantRemovedV1",
    "MatchLineupAssignedV1",
    "MatchCommentAddedV1",
    "MatchCommentDeletedV1",
    "MatchResultUpdatedV1",
    # Nucleo
    "NucleoCreatedData",
    "NucleoUpdatedData",
    "NucleoDeletedData",
    "NucleoCreatedV1",
    "NucleoUpdatedV1",
    "NucleoDeletedV1",
    # Course
    "CourseCreatedData",
    "CourseUpdatedData",
    "CourseDeletedData",
    "CourseCreatedV1",
    "CourseUpdatedV1",
    "CourseDeletedV1",
    # ModalityType
    "ModalityTypeCreatedData",
    "ModalityTypeUpdatedData",
    "ModalityTypeDeletedData",
    "ModalityTypeCreatedV1",
    "ModalityTypeUpdatedV1",
    "ModalityTypeDeletedV1",
    # Modality
    "ModalityCreatedData",
    "ModalityUpdatedData",
    "ModalityDeletedData",
    "ModalityCreatedV1",
    "ModalityUpdatedV1",
    "ModalityDeletedV1",
    # Student
    "StudentCreatedData",
    "StudentUpdatedData",
    "StudentDeletedData",
    "StudentCreatedV1",
    "StudentUpdatedV1",
    "StudentDeletedV1",
    # Staff
    "StaffCreatedData",
    "StaffUpdatedData",
    "StaffDeletedData",
    "StaffCreatedV1",
    "StaffUpdatedV1",
    "StaffDeletedV1",
    # Team
    "TeamCreatedData",
    "TeamUpdatedData",
    "TeamDeletedData",
    "TeamPlayerAddedData",
    "TeamPlayerRemovedData",
    "TeamCreatedV1",
    "TeamUpdatedV1",
    "TeamDeletedV1",
    "TeamPlayerAddedV1",
    "TeamPlayerRemovedV1",
    # Tournament data
    "TournamentCreatedData",
    "TournamentUpdatedData",
    "TournamentDeletedData",
    "TournamentFinishedData",
    "TournamentCompetitorAddedData",
    "TournamentCompetitorDeletedData",
    "RankingEntryData",
    # Tournament schemas
    "TournamentCreatedV1",
    "TournamentUpdatedV1",
    "TournamentDeletedV1",
    "TournamentFinishedV1",
    "TournamentCompetitorAddedV1",
    "TournamentCompetitorDeletedV1",
    "TournamentLeagueStandingsUpdatedV1",
    # Ranking data
    "GeneralRankingEntryData",
    "ModalityRankingEntryData",
    "RankingComputedData",
    # Ranking schemas
    "RankingComputedV1",
    # Regulations schemas
    "RegulationCreatedV1",
    "RegulationUpdatedV1",
    "RegulationDeletedV1",
    # Season schemas
    "SeasonCreatedV1",
]
