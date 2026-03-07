"""
taca-snapshots — Typed snapshot DTO contracts for TACA microservices.

This package contains **Pydantic-only** models that represent the snapshot
payloads exchanged between domain services (providers) and the Read Model
Updater (consumer) during a read-model rebuild.

No SQLAlchemy, no business logic, no repositories — only DTO definitions.

Usage (provider side)::

    from taca_snapshots.matches import (
        MatchSnapshotItem,
        MatchParticipantSnapshotItem,
        MatchesSnapshotResponse,
    )

Usage (consumer side)::

    from taca_snapshots.matches import MatchesSnapshotResponse

    parsed = MatchesSnapshotResponse(**raw_json_dict)
    for match in parsed.matches:
        print(match.match_id, match.status)
"""

from .matches import (
    MatchCommentSnapshotItem,
    MatchesSnapshotResponse,
    MatchLineupSnapshotItem,
    MatchParticipantSnapshotItem,
    MatchResultSnapshotItem,
    MatchSnapshotItem,
)
from .modalities import (
    CourseSnapshotItem,
    ModalitiesSnapshotResponse,
    ModalitySnapshotItem,
    ModalityTypeSnapshotItem,
    NucleoSnapshotItem,
    StaffSnapshotItem,
    StudentSnapshotItem,
    TeamPlayerSnapshotItem,
    TeamSnapshotItem,
)
from .ranking import (
    CourseRankingSnapshotItem,
    GeneralRankingSnapshotItem,
    ModalityRankingSnapshotItem,
    RankingSnapshotResponse,
)
from .tournaments import (
    TournamentCompetitorSnapshotItem,
    TournamentRankingPositionSnapshotItem,
    TournamentSnapshotItem,
    TournamentsSnapshotResponse,
)

__all__ = [
    # base
    # matches
    "MatchSnapshotItem",
    "MatchParticipantSnapshotItem",
    "MatchResultSnapshotItem",
    "MatchLineupSnapshotItem",
    "MatchCommentSnapshotItem",
    "MatchesSnapshotResponse",
    # modalities
    "NucleoSnapshotItem",
    "CourseSnapshotItem",
    "ModalityTypeSnapshotItem",
    "ModalitySnapshotItem",
    "StudentSnapshotItem",
    "StaffSnapshotItem",
    "TeamSnapshotItem",
    "TeamPlayerSnapshotItem",
    "ModalitiesSnapshotResponse",
    # tournaments
    "TournamentSnapshotItem",
    "TournamentCompetitorSnapshotItem",
    "TournamentRankingPositionSnapshotItem",
    "TournamentsSnapshotResponse",
    # ranking
    "ModalityRankingSnapshotItem",
    "CourseRankingSnapshotItem",
    "GeneralRankingSnapshotItem",
    "RankingSnapshotResponse",
]
