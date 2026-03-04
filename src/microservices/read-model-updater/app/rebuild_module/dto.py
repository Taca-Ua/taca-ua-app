"""
Data Transfer Objects (DTOs) for snapshot data.

These DTOs represent the structure of snapshot data received from domain services.
They provide type safety and validation for the rebuild process.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SnapshotMetadata:
    """
    Metadata about a snapshot from a domain service.

    Contains information about when the snapshot was created,
    what service it came from, and how many records it contains.
    """

    service_name: str
    snapshot_timestamp: str
    total_records: int
    version: str = "1.0"


@dataclass
class ServiceSnapshot:
    """
    Complete snapshot data from a single domain service.

    Contains:
    - Metadata about the snapshot
    - Raw data records (as list of dictionaries)
    - Service-specific information
    """

    metadata: SnapshotMetadata
    data: List[Dict[str, Any]]

    @property
    def service_name(self) -> str:
        """Get the service name from metadata."""
        return self.metadata.service_name

    @property
    def record_count(self) -> int:
        """Get the number of records in this snapshot."""
        return len(self.data)

    def validate(self) -> bool:
        """
        Validate snapshot data consistency.

        Returns:
            True if validation passes, False otherwise
        """
        # Check if record count matches metadata
        if self.record_count != self.metadata.total_records:
            return False

        # Check if data is a list
        if not isinstance(self.data, list):
            return False

        return True


@dataclass
class MatchesSnapshot:
    """
    Snapshot data from Matches service.

    Contains matches, participants, results, lineups, and comments.
    """

    matches: List[Dict[str, Any]]
    participants: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    lineups: List[Dict[str, Any]]
    comments: List[Dict[str, Any]]


@dataclass
class TournamentSnapshot:
    """
    Snapshot data from Tournament service.

    Contains tournaments, their competitors, and final rankings.
    """

    tournaments: List[Dict[str, Any]]
    competitors: List[Dict[str, Any]]
    rankings: List[Dict[str, Any]]


@dataclass
class ModalitiesSnapshot:
    """
    Snapshot data from Modalities service.

    Contains modalities, modality types, teams, players, students, etc.
    """

    nucleos: List[Dict[str, Any]]
    courses: List[Dict[str, Any]]
    modality_types: List[Dict[str, Any]]
    modalities: List[Dict[str, Any]]
    students: List[Dict[str, Any]]
    staff: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]
    team_players: List[Dict[str, Any]]


@dataclass
class RankingSnapshot:
    """
    Snapshot data from Ranking service.

    Contains ranking-related data if needed.
    Note: Ranking might be computed, so this may be empty or minimal.
    """

    rankings: List[Dict[str, Any]]


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
    ranking: Optional[RankingSnapshot]

    def has_data(self) -> bool:
        """Check if snapshot contains any data."""
        return any(
            [
                self.matches is not None,
                self.tournament is not None,
                self.modalities is not None,
                self.ranking is not None,
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

        if self.ranking:
            count += len(self.ranking.rankings)

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
