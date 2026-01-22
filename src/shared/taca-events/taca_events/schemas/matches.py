"""
Match service event schemas.
"""

MATCH_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchCreated v1",
    "description": "Event emitted when a new match is created",
    "required": [
        "match_id",
        "tournament_id",
        "team_home_id",
        "team_away_id",
        "start_time",
        "created_at",
    ],
    "properties": {
        "match_id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique identifier for the match",
        },
        "tournament_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the tournament this match belongs to",
        },
        "team_home_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the home team",
        },
        "team_away_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the away team",
        },
        "start_time": {
            "type": "string",
            "format": "date-time",
            "description": "Scheduled start time of the match",
        },
        "location": {"type": "string", "description": "Match location/venue"},
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "When the match record was created",
        },
    },
    "additionalProperties": False,
}

MATCH_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchUpdated v1",
    "description": "Event emitted when match details are updated",
    "required": ["match_id", "changes", "updated_at"],
    "properties": {
        "match_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the updated match",
        },
        "changes": {
            "type": "object",
            "description": "Fields that were changed",
            "minProperties": 1,
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "When the match was updated",
        },
    },
    "additionalProperties": False,
}

MATCH_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchDeleted v1",
    "description": "Event emitted when a match is deleted",
    "required": ["match_id", "deleted_at"],
    "properties": {
        "match_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the deleted match",
        },
        "reason": {"type": "string", "description": "Reason for deletion"},
        "deleted_at": {
            "type": "string",
            "format": "date-time",
            "description": "When the match was deleted",
        },
    },
    "additionalProperties": False,
}

MATCH_FINISHED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchFinished v1",
    "description": "Event emitted when a match is completed with final results",
    "required": [
        "match_id",
        "tournament_id",
        "team_home_id",
        "team_away_id",
        "home_score",
        "away_score",
        "finished_at",
    ],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "tournament_id": {"type": "string", "format": "uuid"},
        "team_home_id": {"type": "string", "format": "uuid"},
        "team_away_id": {"type": "string", "format": "uuid"},
        "home_score": {
            "type": "integer",
            "minimum": 0,
            "description": "Final score for home team",
        },
        "away_score": {
            "type": "integer",
            "minimum": 0,
            "description": "Final score for away team",
        },
        "finished_at": {"type": "string", "format": "date-time"},
        "winner_id": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "ID of winning team, null for draw",
        },
    },
    "additionalProperties": False,
}

MATCH_PARTICIPANT_ADDED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchParticipantAdded v1",
    "description": "Event emitted when a participant is added to a match",
    "required": ["match_id", "participant_id", "team_id", "added_at"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "participant_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the participant (student/staff)",
        },
        "team_id": {
            "type": "string",
            "format": "uuid",
            "description": "Which team the participant plays for",
        },
        "added_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MATCH_PARTICIPANT_REMOVED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchParticipantRemoved v1",
    "description": "Event emitted when a participant is removed from a match",
    "required": ["match_id", "participant_id", "removed_at"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "participant_id": {"type": "string", "format": "uuid"},
        "reason": {"type": "string", "description": "Reason for removal"},
        "removed_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MATCH_RESULT_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchResultUpdated v1",
    "description": "Event emitted when match results/scores are updated",
    "required": ["match_id", "home_score", "away_score", "updated_at"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "home_score": {"type": "integer", "minimum": 0},
        "away_score": {"type": "integer", "minimum": 0},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MATCH_LINEUP_ASSIGNED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchLineupAssigned v1",
    "description": "Event emitted when a team lineup is assigned for a match",
    "required": ["match_id", "team_id", "lineup", "assigned_at"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "team_id": {"type": "string", "format": "uuid"},
        "lineup": {
            "type": "array",
            "items": {"type": "string", "format": "uuid"},
            "description": "List of participant IDs in the lineup",
        },
        "assigned_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MATCH_COMMENT_ADDED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchCommentAdded v1",
    "description": "Event emitted when a comment is added to a match",
    "required": ["match_id", "comment_id", "content", "created_at"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "comment_id": {"type": "string", "format": "uuid"},
        "content": {"type": "string", "description": "Comment text content"},
        "created_by": {
            "type": "string",
            "format": "uuid",
            "description": "ID of user who created the comment",
        },
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MATCH_COMMENT_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchCommentDeleted v1",
    "description": "Event emitted when a comment is deleted from a match",
    "required": ["match_id", "comment_id", "deleted_at"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "comment_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# Export all match schemas
MATCH_SCHEMAS = {
    "match.created.v1": MATCH_CREATED_V1,
    "match.updated.v1": MATCH_UPDATED_V1,
    "match.deleted.v1": MATCH_DELETED_V1,
    "match.finished.v1": MATCH_FINISHED_V1,
    "match.participant.added.v1": MATCH_PARTICIPANT_ADDED_V1,
    "match.participant.removed.v1": MATCH_PARTICIPANT_REMOVED_V1,
    "match.result.updated.v1": MATCH_RESULT_UPDATED_V1,
    "match.lineup.assigned.v1": MATCH_LINEUP_ASSIGNED_V1,
    "match.comment.added.v1": MATCH_COMMENT_ADDED_V1,
    "match.comment.deleted.v1": MATCH_COMMENT_DELETED_V1,
}
