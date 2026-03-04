"""
Tournament service event schemas.
"""

TOURNAMENT_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentCreated v1",
    "description": "Event emitted when a new tournament is created",
    "required": ["tournament_id", "modality_id", "name", "start_date", "status"],
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
        "name": {"type": "string", "description": "Tournament name"},
        "start_date": {
            "type": "string",
            "format": "date",
            "description": "Tournament start date",
        },
        "status": {
            "type": "string",
            "description": "Tournament status (e.g., draft, active, finished)",
        },
    },
    "additionalProperties": False,
}

TOURNAMENT_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentUpdated v1",
    "description": "Event emitted when tournament details are updated",
    "required": ["tournament_id"],
    "properties": {
        "tournament_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "start_date": {"type": "string", "format": "date"},
        "status": {"type": "string"},
    },
    "additionalProperties": False,
}

TOURNAMENT_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentDeleted v1",
    "description": "Event emitted when a tournament is deleted",
    "required": ["tournament_id"],
    "properties": {
        "tournament_id": {"type": "string", "format": "uuid"},
    },
    "additionalProperties": False,
}

TOURNAMENT_FINISHED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentFinished v1",
    "description": "Event emitted when a tournament is completed",
    "required": ["tournament_id", "ranking_entries"],
    "properties": {
        "tournament_id": {"type": "string", "format": "uuid"},
        "ranking_entries": {
            "type": "array",
            "description": "Final ranking of teams in the tournament",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["team_id", "position"],
                "properties": {
                    "team_id": {"type": "string", "format": "uuid"},
                    "position": {"type": "integer"},
                },
            },
        },
    },
    "additionalProperties": False,
}

TOURNAMENT_COMPETITOR_ADDED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentCompetitorAdded v1",
    "description": "Event emitted when a competitor is added to a tournament",
    "required": ["tournament_id", "competitor_type", "competitor_entity_id"],
    "properties": {
        "tournament_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the tournament to which the competitor was added",
        },
        "competitor_type": {
            "type": "string",
            "enum": ["team", "athlete"],
            "description": "Type of the competitor (team or athlete)",
        },
        "competitor_entity_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the team or athlete competitor entity",
        },
    },
    "additionalProperties": False,
}

TOURNAMENT_COMPETITOR_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TournamentCompetitorDeleted v1",
    "description": "Event emitted when a competitor is removed from a tournament",
    "required": ["competitor_id", "tournament_id"],
    "properties": {
        "competitor_id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique identifier for the tournament competitor",
        },
        "tournament_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of the tournament from which the competitor was removed",
        },
    },
    "additionalProperties": False,
}

# Export all tournament schemas
TOURNAMENT_SCHEMAS = {
    "tournament.created.v1": TOURNAMENT_CREATED_V1,
    "tournament.updated.v1": TOURNAMENT_UPDATED_V1,
    "tournament.deleted.v1": TOURNAMENT_DELETED_V1,
    "tournament.finished.v1": TOURNAMENT_FINISHED_V1,
    "tournament.competitor.deleted.v1": TOURNAMENT_COMPETITOR_DELETED_V1,
    "tournament.competitor.added.v1": TOURNAMENT_COMPETITOR_ADDED_V1,
}
