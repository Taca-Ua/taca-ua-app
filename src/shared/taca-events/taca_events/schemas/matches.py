"""
Match service event schemas.
"""

_LINEUP_PLAYER_V1 = {
    "type": "object",
    "required": ["player_id", "jersey_number", "is_starter"],
    "properties": {
        "player_id": {"type": "string", "format": "uuid"},
        "jersey_number": {"type": "integer", "minimum": 0},
        "is_starter": {"type": "boolean"},
    },
    "additionalProperties": False,
}

_MATCH_RESULT_ITEM_V1 = {
    "type": "object",
    "required": ["participant_id"],
    "properties": {
        "participant_id": {"type": "string", "format": "uuid"},
        "score": {
            "type": ["integer", "null"],
            "minimum": 0,
            "description": "Score of the participant",
        },
        "position": {
            "type": ["integer", "null"],
            "description": "Position of the participant in the match",
        },
        "results_metadata": {
            "type": ["object", "null"],
            "description": "Additional metadata about the participant's results",
        },
    },
    "additionalProperties": False,
}


MATCH_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchCreated v1",
    "description": "Event emitted when a new match is created",
    "required": [
        "match_id",
        "tournament_id",
        "location",
        "status",
        "start_time",
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
        "location": {"type": "string", "description": "Match location/venue"},
        "status": {
            "type": "string",
            "enum": ["scheduled", "in_progress", "completed", "cancelled"],
            "description": "Current status of the match",
        },
        "start_time": {
            "type": "string",
            "format": "date-time",
            "description": "Scheduled start time of the match",
        },
        "participants": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "participant_id",
                    "participant_type",
                    "participant_entity_id",
                ],
                "properties": {
                    "participant_id": {"type": "string", "format": "uuid"},
                    "participant_type": {
                        "type": "string",
                        "enum": ["team", "athlete"],
                        "description": "Type of participant",
                    },
                    "participant_entity_id": {"type": "string", "format": "uuid"},
                },
                "additionalProperties": False,
            },
            "description": "List of participants in the match",
        },
    },
    "additionalProperties": False,
}

MATCH_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchUpdated v1",
    "description": "Event emitted when match details are updated",
    "required": ["match_id"],
    "properties": {
        "match_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the updated match",
        },
        "location": {"type": "string", "description": "Updated match location/venue"},
        "start_time": {
            "type": "string",
            "format": "date-time",
            "description": "Updated scheduled start time of the match",
        },
        "status": {
            "type": "string",
            "enum": ["scheduled", "in_progress", "finished", "cancelled"],
            "description": "Updated status of the match",
        },
    },
    "additionalProperties": False,
}

MATCH_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchDeleted v1",
    "description": "Event emitted when a match is deleted",
    "required": ["match_id"],
    "properties": {
        "match_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the deleted match",
        },
    },
    "additionalProperties": False,
}

MATCH_PARTICIPANT_ADDED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchParticipantAdded v1",
    "description": "Event emitted when a participant is added to a match",
    "required": [
        "match_id",
        "participant_id",
        "participant_type",
        "participant_entity_id",
    ],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "participant_id": {"type": "string", "format": "uuid"},
        "participant_type": {
            "type": "string",
            "enum": ["team", "athlete"],
            "description": "Type of participant being added",
        },
        "participant_entity_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the participant entity (team or athlete)",
        },
    },
    "additionalProperties": False,
}

MATCH_PARTICIPANT_REMOVED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchParticipantRemoved v1",
    "description": "Event emitted when a participant is removed from a match",
    "required": ["match_id", "participant_id"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "participant_id": {"type": "string", "format": "uuid"},
    },
    "additionalProperties": False,
}

MATCH_RESULT_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchResultUpdated v1",
    "description": "Event emitted when match results/scores are updated",
    "required": ["match_id", "results"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "results": {
            "type": "array",
            "items": _MATCH_RESULT_ITEM_V1,
            "description": "List of participant results",
        },
    },
    "additionalProperties": False,
}

MATCH_LINEUP_ASSIGNED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchLineupAssigned v1",
    "description": "Event emitted when a team lineup is assigned for a match",
    "required": ["match_id", "team_id", "lineup"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "team_id": {"type": "string", "format": "uuid"},
        "lineup": {
            "type": "array",
            "minItems": 1,
            "items": _LINEUP_PLAYER_V1,
            "description": "List of participant IDs in the lineup",
        },
    },
    "additionalProperties": False,
}

MATCH_COMMENT_ADDED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchCommentAdded v1",
    "description": "Event emitted when a comment is added to a match",
    "required": ["comment_id", "match_id", "message"],
    "properties": {
        "comment_id": {"type": "string", "format": "uuid"},
        "match_id": {"type": "string", "format": "uuid"},
        "message": {"type": "string", "description": "Comment text content"},
    },
    "additionalProperties": False,
}

MATCH_COMMENT_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "MatchCommentDeleted v1",
    "description": "Event emitted when a comment is deleted from a match",
    "required": ["match_id", "comment_id"],
    "properties": {
        "match_id": {"type": "string", "format": "uuid"},
        "comment_id": {"type": "string", "format": "uuid"},
    },
    "additionalProperties": False,
}

# Export all match schemas
MATCH_SCHEMAS = {
    "match.created.v1": MATCH_CREATED_V1,
    "match.updated.v1": MATCH_UPDATED_V1,
    "match.deleted.v1": MATCH_DELETED_V1,
    "match.participant.added.v1": MATCH_PARTICIPANT_ADDED_V1,
    "match.participant.removed.v1": MATCH_PARTICIPANT_REMOVED_V1,
    "match.result.updated.v1": MATCH_RESULT_UPDATED_V1,
    "match.lineup.assigned.v1": MATCH_LINEUP_ASSIGNED_V1,
    "match.comment.added.v1": MATCH_COMMENT_ADDED_V1,
    "match.comment.deleted.v1": MATCH_COMMENT_DELETED_V1,
}


"""

		"score": {
            "type": "integer",
            "minimum": 0,
            "description": "Score of the participant at removal time",
        },
		"position": {
            "type": "string",
            "description": "Position of the participant in the match",
        },
		"results_metadata": {
            "type": "object",
            "description": "Additional metadata about the participant's results",
        },

"""
