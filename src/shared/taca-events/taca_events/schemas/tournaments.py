"""
Tournament service event schemas.
"""

TOURNAMENT_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentCreated v1",
    "description": "Event emitted when a new tournament is created",
    "required": ["tournament_id", "modality_id", "season_id", "name", "created_at"],
    "properties": {
        "tournament_id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique identifier for the tournament",
        },
        "modality_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the modality (sport type)",
        },
        "season_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the season",
        },
        "name": {"type": "string", "description": "Tournament name"},
        "description": {"type": "string", "description": "Tournament description"},
        "start_date": {
            "type": "string",
            "format": "date",
            "description": "Tournament start date",
        },
        "end_date": {
            "type": "string",
            "format": "date",
            "description": "Tournament end date",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "When the tournament was created",
        },
    },
    "additionalProperties": False,
}

TOURNAMENT_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentUpdated v1",
    "description": "Event emitted when tournament details are updated",
    "required": ["tournament_id", "changes", "updated_at"],
    "properties": {
        "tournament_id": {"type": "string", "format": "uuid"},
        "changes": {
            "type": "object",
            "description": "Fields that were changed",
            "minProperties": 1,
        },
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

TOURNAMENT_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentDeleted v1",
    "description": "Event emitted when a tournament is deleted",
    "required": ["tournament_id", "deleted_at"],
    "properties": {
        "tournament_id": {"type": "string", "format": "uuid"},
        "reason": {"type": "string", "description": "Reason for deletion"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

TOURNAMENT_FINISHED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentFinished v1",
    "description": "Event emitted when a tournament is completed",
    "required": ["tournament_id", "modality_id", "season_id", "finished_at"],
    "properties": {
        "tournament_id": {"type": "string", "format": "uuid"},
        "modality_id": {"type": "string", "format": "uuid"},
        "season_id": {"type": "string", "format": "uuid"},
        "winner_team_id": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "ID of the winning team, null if no clear winner",
        },
        "finished_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# Export all tournament schemas
TOURNAMENT_SCHEMAS = {
    "tournament.created.v1": TOURNAMENT_CREATED_V1,
    "tournament.updated.v1": TOURNAMENT_UPDATED_V1,
    "tournament.deleted.v1": TOURNAMENT_DELETED_V1,
    "tournament.finished.v1": TOURNAMENT_FINISHED_V1,
}
