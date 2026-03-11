"""
Data Transfer Objects (DTOs) for snapshot data.

These DTOs represent the structure of snapshot data received from domain services.
The per-entity items are strongly typed Pydantic models imported from the shared
``taca-snapshots`` package; only the aggregate containers and rebuild result are
defined here as dataclasses so that the rest of the rebuild orchestration code is
unchanged.
"""

from dataclasses import dataclass
from typing import List, Optional

from taca_snapshots.matches import (
    MatchCommentSnapshotItem,
    MatchesSnapshotResponse,
    MatchLineupSnapshotItem,
    MatchParticipantSnapshotItem,
    MatchResultSnapshotItem,
    MatchSnapshotItem,
)
from taca_snapshots.modalities import (
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
from taca_snapshots.tournaments import (
    TournamentCompetitorSnapshotItem,
    TournamentRankingPositionSnapshotItem,
    TournamentSnapshotItem,
    TournamentsSnapshotResponse,
)

# Re-export individual item types so callers can import from this module
__all__ = [
    "MatchSnapshotItem",
    "MatchParticipantSnapshotItem",
    "MatchResultSnapshotItem",
    "MatchLineupSnapshotItem",
    "MatchCommentSnapshotItem",
    "NucleoSnapshotItem",
    "CourseSnapshotItem",
    "ModalityTypeSnapshotItem",
    "ModalitySnapshotItem",
    "StudentSnapshotItem",
    "StaffSnapshotItem",
    "TeamSnapshotItem",
    "TeamPlayerSnapshotItem",
    "TournamentSnapshotItem",
    "TournamentCompetitorSnapshotItem",
    "TournamentRankingPositionSnapshotItem",
    "MatchesSnapshot",
    "TournamentSnapshot",
    "ModalitiesSnapshot",
    "CompleteSnapshot",
    "RebuildResult",
]


@dataclass
class MatchesSnapshot:
    """
    Snapshot data from Matches service, using strongly typed item DTOs.
    """

    matches: List[MatchSnapshotItem]
    participants: List[MatchParticipantSnapshotItem]
    results: List[MatchResultSnapshotItem]
    lineups: List[MatchLineupSnapshotItem]
    comments: List[MatchCommentSnapshotItem]

    @classmethod
    def from_response(cls, response: MatchesSnapshotResponse) -> "MatchesSnapshot":
        """Build from a parsed MatchesSnapshotResponse."""
        return cls(
            matches=response.matches,
            participants=response.participants,
            results=response.results,
            lineups=response.lineups,
            comments=response.comments,
        )


@dataclass
class TournamentSnapshot:
    """
    Snapshot data from Tournament service, using strongly typed item DTOs.

    Note: the field is named ``rankings`` here (matching existing rebuild code)
    even though the service endpoint serialises the list under ``ranking_positions``.
    The snapshot client handles the mapping.
    """

    tournaments: List[TournamentSnapshotItem]
    competitors: List[TournamentCompetitorSnapshotItem]
    rankings: List[TournamentRankingPositionSnapshotItem]

    @classmethod
    def from_response(
        cls, response: TournamentsSnapshotResponse
    ) -> "TournamentSnapshot":
        """Build from a parsed TournamentsSnapshotResponse."""
        return cls(
            tournaments=response.tournaments,
            competitors=response.competitors,
            rankings=response.ranking_positions,
        )


@dataclass
class ModalitiesSnapshot:
    """
    Snapshot data from Modalities service, using strongly typed item DTOs.
    """

    nucleos: List[NucleoSnapshotItem]
    courses: List[CourseSnapshotItem]
    modality_types: List[ModalityTypeSnapshotItem]
    modalities: List[ModalitySnapshotItem]
    students: List[StudentSnapshotItem]
    staff: List[StaffSnapshotItem]
    teams: List[TeamSnapshotItem]
    team_players: List[TeamPlayerSnapshotItem]

    @classmethod
    def from_response(
        cls, response: ModalitiesSnapshotResponse
    ) -> "ModalitiesSnapshot":
        """Build from a parsed ModalitiesSnapshotResponse."""
        return cls(
            nucleos=response.nucleos,
            courses=response.courses,
            modality_types=response.modality_types,
            modalities=response.modalities,
            students=response.students,
            staff=response.staff,
            teams=response.teams,
            team_players=response.team_players,
        )


@dataclass
class CompleteSnapshot:
    """
    Aggregated snapshot from all domain services.

    This represents the complete state of the system that will be used
    to rebuild all projection tables.
    """

    matches: Optional[MatchesSnapshot]
    tournament: Optional[TournamentSnapshot]
    modalities: Optional[ModalitiesSnapshot]

    def has_data(self) -> bool:
        """Check if snapshot contains any data."""
        return any(
            [
                self.matches is not None,
                self.tournament is not None,
                self.modalities is not None,
            ]
        )

    def get_total_record_count(self) -> int:
        """Calculate total number of records across all snapshots."""
        count = 0

        if self.matches:
            count += (
                len(self.matches.matches)
                + len(self.matches.participants)
                + len(self.matches.results)
                + len(self.matches.lineups)
                + len(self.matches.comments)
            )

        if self.tournament:
            count += (
                len(self.tournament.tournaments)
                + len(self.tournament.competitors)
                + len(self.tournament.rankings)
            )

        if self.modalities:
            count += (
                len(self.modalities.nucleos)
                + len(self.modalities.courses)
                + len(self.modalities.modality_types)
                + len(self.modalities.modalities)
                + len(self.modalities.students)
                + len(self.modalities.staff)
                + len(self.modalities.teams)
                + len(self.modalities.team_players)
            )

        return count


@dataclass
class RebuildResult:
    """
    Result of a rebuild operation.

    Contains information about success/failure,
    number of records processed, and any errors encountered.
    """

    success: bool
    message: str
    records_processed: int
    duration_seconds: float
    errors: List[str]

    def add_error(self, error: str) -> None:
        """Add an error message to the result."""
        self.errors.append(error)
        self.success = False
