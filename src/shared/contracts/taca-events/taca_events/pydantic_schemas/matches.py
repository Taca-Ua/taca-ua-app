"""
Typed Pydantic event schemas for the Matches Service.

These models represent the typed ``data`` payload of each match-domain event.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .base import EventSchema

# ================================================================== #
# Data payload models
# ================================================================== #


class MatchParticipantData(BaseModel):
    """Participant entry embedded in MatchCreatedData."""

    participant_id: UUID
    participant_type: Optional[str]  # "team" | "athlete"
    participant_entity_id: Optional[UUID]


class MatchCreatedData(BaseModel):
    match_id: UUID
    tournament_id: Optional[UUID] = None
    location: str
    status: str
    start_time: str  # ISO 8601
    participants: List[MatchParticipantData] = []


class MatchUpdatedData(BaseModel):
    match_id: UUID
    location: Optional[str] = None
    start_time: Optional[str] = None
    status: Optional[str] = None


class MatchDeletedData(BaseModel):
    match_id: UUID


class MatchParticipantAddedData(BaseModel):
    match_id: UUID
    participant_id: UUID
    participant_type: str
    participant_entity_id: UUID


class MatchParticipantRemovedData(BaseModel):
    match_id: UUID
    participant_id: UUID


class LineupPlayerData(BaseModel):
    """Player entry embedded in MatchLineupAssignedData."""

    player_id: UUID
    jersey_number: int
    is_starter: bool


class MatchLineupAssignedData(BaseModel):
    match_id: UUID
    team_id: UUID
    lineup: List[LineupPlayerData] = []


class MatchCommentAddedData(BaseModel):
    comment_id: UUID
    match_id: UUID
    message: str


class MatchCommentDeletedData(BaseModel):
    comment_id: UUID
    match_id: UUID


class MatchResultEntryData(BaseModel):
    """Result entry for one participant."""

    participant_id: UUID
    score: Optional[int] = None
    position: Optional[int] = None
    results_metadata: Optional[dict] = None


class MatchResultUpdatedData(BaseModel):
    match_id: UUID
    results: List[MatchResultEntryData] = []


# ================================================================== #
# EventSchema subclasses
# ================================================================== #


class MatchCreatedV1(EventSchema):
    data: MatchCreatedData

    @classmethod
    def event_type(cls) -> str:
        return "match.created.v1"


class MatchUpdatedV1(EventSchema):
    data: MatchUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "match.updated.v1"


class MatchDeletedV1(EventSchema):
    data: MatchDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "match.deleted.v1"


class MatchParticipantAddedV1(EventSchema):
    data: MatchParticipantAddedData

    @classmethod
    def event_type(cls) -> str:
        return "match.participant.added.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "match"


class MatchParticipantRemovedV1(EventSchema):
    data: MatchParticipantRemovedData

    @classmethod
    def event_type(cls) -> str:
        return "match.participant.removed.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "match"


class MatchLineupAssignedV1(EventSchema):
    data: MatchLineupAssignedData

    @classmethod
    def event_type(cls) -> str:
        return "match.lineup.assigned.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "match"


class MatchCommentAddedV1(EventSchema):
    data: MatchCommentAddedData

    @classmethod
    def event_type(cls) -> str:
        return "match.comment.added.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "match"


class MatchCommentDeletedV1(EventSchema):
    data: MatchCommentDeletedData

    @classmethod
    def event_type(cls) -> str:
        return "match.comment.deleted.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "match"


class MatchResultUpdatedV1(EventSchema):
    data: MatchResultUpdatedData

    @classmethod
    def event_type(cls) -> str:
        return "match.result.updated.v1"

    @classmethod
    def aggregate_type(cls) -> str:
        return "match"
