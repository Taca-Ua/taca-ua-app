"""
SQLAlchemy models for Matches Service.
Schema: matches
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship
from taca_outbox.models import create_outbox_model
from taca_snapshots import matches

Base = declarative_base()


class MatchStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Match(Base):
    """
    A single competitive occurrence.
    No assumptions about sport, modality, or structure.
    """

    __tablename__ = "match"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to tournament domain
    tournament_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    location = Column(Text, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)

    status = Column(
        Enum(MatchStatus, name="match_status", inherit_schema=True),
        nullable=False,
        default=MatchStatus.SCHEDULED,
    )
    journey = Column(
        Integer, nullable=False
    )  # way to group matches in a tournament (e.g., round number)

    # Bullsh*t fields for auditing and traceability
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )

    participants: Mapped[list["MatchParticipant"]] = relationship(
        "MatchParticipant",
        back_populates="match",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="match",
        cascade="all, delete-orphan",
    )
    lineups: Mapped[list["Lineup"]] = relationship(
        "Lineup",
        back_populates="match",
        cascade="all, delete-orphan",
    )
    staff_assignments: Mapped[list["MatchLineupStaff"]] = relationship(
        "MatchLineupStaff",
        back_populates="match",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Match {self.id} status={self.status.value}>"

    def to_dict(self, include_details: bool = False) -> dict:
        """Convert Match to dictionary for API responses"""
        lineups_response = []
        if include_details:
            lineups_per_participant = {
                participant_id: []
                for participant_id in {str(p.participant) for p in self.participants}
            }
            for lineup in self.lineups:
                if str(lineup.participant) not in lineups_per_participant:
                    lineups_per_participant[str(lineup.participant)] = []
                lineups_per_participant[str(lineup.participant)].append(
                    {
                        "player_id": str(lineup.player_id),
                        "jersey_number": lineup.jersey_number,
                        "is_starter": lineup.is_starter,
                    }
                )

            for participant_id, lineup in lineups_per_participant.items():
                lineups_response.append(
                    {
                        "participant_id": participant_id,
                        "lineup": lineup,
                    }
                )

            staff_assignments_per_participant = {
                participant_id: []
                for participant_id in {str(p.participant) for p in self.participants}
            }
            for assignment in self.staff_assignments:
                if (
                    str(assignment.participant_id)
                    not in staff_assignments_per_participant
                ):
                    staff_assignments_per_participant[
                        str(assignment.participant_id)
                    ] = []
                staff_assignments_per_participant[
                    str(assignment.participant_id)
                ].append(str(assignment.staff_id))

        return {
            "id": str(self.id),
            "tournament_id": str(self.tournament_id),
            "location": self.location,
            "start_time": self.start_time.isoformat(),
            "status": self.status.value,
            "journey": self.journey,
            "participants": [p.to_dict() for p in self.participants],
            "comments": (
                [
                    {
                        "id": str(c.id),
                        "message": c.message,
                        "created_at": c.created_at.isoformat(),
                        "created_by": str(c.created_by),
                    }
                    for c in self.comments
                ]
                if include_details
                else []
            ),
            "lineups": lineups_response if include_details else [],
            "staff_assignments": (
                staff_assignments_per_participant if include_details else None
            ),
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_snapshot(self) -> matches.MatchSnapshotItem:
        """Convert Match to snapshot item for internal API"""
        return matches.MatchSnapshotItem(
            match_id=str(self.id),
            tournament_id=str(self.tournament_id) if self.tournament_id else None,
            location=self.location,
            status=self.status.value if self.status else None,
            start_time=self.start_time,
            journey=self.journey,  # Include the journey field in the snapshot
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=None,  # Domain model doesn't track deletions
        )


class MatchParticipant(Base):
    """
    Represents one participant in a match and its outcome.
    """

    __tablename__ = "match_participant"
    __table_args__ = {"schema": "matches"}

    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("matches.match.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        primary_key=True,
    )

    # Reference to the competitor of the tournament domain
    participant = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        primary_key=True,
    )

    # Outcome
    score = Column(Integer, nullable=True)
    position = Column(Integer, nullable=True)

    match: Mapped[Match] = relationship("Match", back_populates="participants")

    def __repr__(self) -> str:
        return (
            f"<MatchParticipant match={self.match_id} participant={self.participant}>"
        )

    def to_dict(self) -> dict:
        return {
            "match_id": str(self.match_id),
            "participant": str(self.participant),
            "score": self.score,
            "position": self.position,
        }

    def to_snapshot(self) -> matches.MatchParticipantSnapshotItem:
        """Convert MatchParticipant to snapshot item for internal API"""
        return matches.MatchParticipantSnapshotItem(
            participant_id=str(self.participant),
            match_id=str(self.match_id),
            participant_type=None,  # No longer tracked in domain model
            participant_entity_id=None,  # No longer tracked in domain model
            added_at=None,  # Domain model doesn't track this
            removed_at=None,
        )

    def to_result_snapshot(self) -> matches.MatchResultSnapshotItem:
        """Convert MatchParticipant to MatchResult snapshot item for internal API"""
        return matches.MatchResultSnapshotItem(
            participant_id=str(self.participant),
            match_id=str(self.match_id),
            score=self.score,
            position=self.position,
        )


class Lineup(Base):
    """
    Stores lineup / roster information for team-based matches.
    """

    __tablename__ = "lineup"
    __table_args__ = {"schema": "matches"}

    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("matches.match.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        primary_key=True,
    )

    # Reference to the participant of the tournament domain
    participant = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        primary_key=True,
    )

    # Student / Athlete Service reference
    player_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        primary_key=True,
    )

    jersey_number = Column(Integer, nullable=True)
    is_starter = Column(Boolean, nullable=True, default=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    match: Mapped[Match] = relationship("Match", back_populates="lineups")

    def __repr__(self) -> str:
        return f"<Lineup match={self.match_id} participant={self.participant} player={self.player_id}>"

    def to_snapshot(self) -> matches.MatchLineupSnapshotItem:
        """Convert Lineup to snapshot item for internal API"""
        return matches.MatchLineupSnapshotItem(
            match_id=str(self.match_id),
            participant_id=str(self.participant),
            player_id=str(self.player_id),
            jersey_number=self.jersey_number,
            is_starter=self.is_starter,
            created_at=self.created_at,
        )


class MatchLineupStaff(Base):
    """
    Stores staff assignments for team-based matches.
    """

    __tablename__ = "lineup_staff"
    __table_args__ = {"schema": "matches"}

    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("matches.match.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        primary_key=True,
    )

    participant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        primary_key=True,
    )

    staff_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        primary_key=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    match: Mapped[Match] = relationship("Match", back_populates="staff_assignments")

    def __repr__(self) -> str:
        return f"<MatchLineupStaff match={self.match_id} participant={self.participant_id} staff={self.staff_id}>"


class Comment(Base):
    """
    Commentary or notes attached to a match.
    """

    __tablename__ = "comment"
    __table_args__ = {"schema": "matches"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_id = Column(
        UUID(as_uuid=True),
        ForeignKey("matches.match.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)

    match: Mapped[Match] = relationship("Match", back_populates="comments")

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Comment {self.id} on match={self.match_id}>"

    def to_snapshot(self) -> matches.MatchCommentSnapshotItem:
        """Convert Comment to snapshot item for internal API"""
        return matches.MatchCommentSnapshotItem(
            comment_id=str(self.id),
            match_id=str(self.match_id),
            message=self.message,
            created_by=str(self.created_by),
            created_at=self.created_at,
        )


# OutboxEvent model — schema-bound via shared factory
OutboxEvent = create_outbox_model(Base, schema="matches")
