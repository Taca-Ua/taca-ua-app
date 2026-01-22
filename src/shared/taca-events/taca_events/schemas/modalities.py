"""
Modalities service event schemas.
"""

# ==================== Nucleo Events ====================

NUCLEO_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "NucleoCreated v1",
    "description": "Event emitted when a new nucleo (organizational unit) is created",
    "required": ["nucleo_id", "name", "abbreviation", "created_at"],
    "properties": {
        "nucleo_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string", "description": "Nucleo name"},
        "abbreviation": {"type": "string", "description": "Nucleo abbreviation"},
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

NUCLEO_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "NucleoUpdated v1",
    "required": ["nucleo_id", "changes", "updated_at"],
    "properties": {
        "nucleo_id": {"type": "string", "format": "uuid"},
        "changes": {"type": "object", "minProperties": 1},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

NUCLEO_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "NucleoDeleted v1",
    "required": ["nucleo_id", "deleted_at"],
    "properties": {
        "nucleo_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# ==================== Course Events ====================

COURSE_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "CourseCreated v1",
    "description": "Event emitted when a new course is created",
    "required": ["course_id", "nucleo_id", "name", "created_at"],
    "properties": {
        "course_id": {"type": "string", "format": "uuid"},
        "nucleo_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

COURSE_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "CourseUpdated v1",
    "required": ["course_id", "changes", "updated_at"],
    "properties": {
        "course_id": {"type": "string", "format": "uuid"},
        "changes": {"type": "object", "minProperties": 1},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

COURSE_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "CourseDeleted v1",
    "required": ["course_id", "deleted_at"],
    "properties": {
        "course_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# ==================== Modality Type Events ====================

MODALITY_TYPE_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "ModalityTypeCreated v1",
    "description": "Event emitted when a new modality type (sport type) is created",
    "required": ["modality_type_id", "name", "created_at"],
    "properties": {
        "modality_type_id": {"type": "string", "format": "uuid"},
        "name": {
            "type": "string",
            "description": "Sport name (e.g., Football, Basketball)",
        },
        "description": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MODALITY_TYPE_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "ModalityTypeUpdated v1",
    "required": ["modality_type_id", "changes", "updated_at"],
    "properties": {
        "modality_type_id": {"type": "string", "format": "uuid"},
        "changes": {"type": "object", "minProperties": 1},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MODALITY_TYPE_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "ModalityTypeDeleted v1",
    "required": ["modality_type_id", "deleted_at"],
    "properties": {
        "modality_type_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# ==================== Modality Events ====================

MODALITY_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "ModalityCreated v1",
    "description": "Event emitted when a new modality is created",
    "required": ["modality_id", "modality_type_id", "season_id", "created_at"],
    "properties": {
        "modality_id": {"type": "string", "format": "uuid"},
        "modality_type_id": {"type": "string", "format": "uuid"},
        "season_id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MODALITY_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "ModalityUpdated v1",
    "required": ["modality_id", "changes", "updated_at"],
    "properties": {
        "modality_id": {"type": "string", "format": "uuid"},
        "changes": {"type": "object", "minProperties": 1},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

MODALITY_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "ModalityDeleted v1",
    "required": ["modality_id", "deleted_at"],
    "properties": {
        "modality_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# ==================== Student Events ====================

STUDENT_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "StudentCreated v1",
    "description": "Event emitted when a new student is registered",
    "required": [
        "student_id",
        "course_id",
        "student_number",
        "full_name",
        "created_at",
    ],
    "properties": {
        "student_id": {"type": "string", "format": "uuid"},
        "course_id": {"type": "string", "format": "uuid"},
        "student_number": {"type": "string"},
        "full_name": {"type": "string"},
        "is_member": {
            "type": "boolean",
            "description": "Whether student is association member",
        },
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

STUDENT_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "StudentUpdated v1",
    "required": ["student_id", "changes", "updated_at"],
    "properties": {
        "student_id": {"type": "string", "format": "uuid"},
        "changes": {"type": "object", "minProperties": 1},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

STUDENT_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "StudentDeleted v1",
    "required": ["student_id", "deleted_at"],
    "properties": {
        "student_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# ==================== Staff Events ====================

STAFF_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "StaffCreated v1",
    "description": "Event emitted when a new staff member is registered",
    "required": ["staff_id", "full_name", "created_at"],
    "properties": {
        "staff_id": {"type": "string", "format": "uuid"},
        "full_name": {"type": "string"},
        "role": {"type": "string", "description": "Staff role"},
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

STAFF_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "StaffUpdated v1",
    "required": ["staff_id", "changes", "updated_at"],
    "properties": {
        "staff_id": {"type": "string", "format": "uuid"},
        "changes": {"type": "object", "minProperties": 1},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

STAFF_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "StaffDeleted v1",
    "required": ["staff_id", "deleted_at"],
    "properties": {
        "staff_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# ==================== Team Events ====================

TEAM_CREATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TeamCreated v1",
    "description": "Event emitted when a new team is created",
    "required": ["team_id", "modality_id", "name", "created_at"],
    "properties": {
        "team_id": {"type": "string", "format": "uuid"},
        "modality_id": {"type": "string", "format": "uuid"},
        "course_id": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "Course ID if team is course-specific",
        },
        "name": {"type": "string"},
        "description": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

TEAM_UPDATED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TeamUpdated v1",
    "required": ["team_id", "changes", "updated_at"],
    "properties": {
        "team_id": {"type": "string", "format": "uuid"},
        "changes": {"type": "object", "minProperties": 1},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

TEAM_DELETED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TeamDeleted v1",
    "required": ["team_id", "deleted_at"],
    "properties": {
        "team_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

TEAM_PLAYER_ADDED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TeamPlayerAdded v1",
    "description": "Event emitted when a player is added to a team",
    "required": ["team_id", "player_id", "added_at"],
    "properties": {
        "team_id": {"type": "string", "format": "uuid"},
        "player_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of student or staff member",
        },
        "player_type": {
            "type": "string",
            "enum": ["student", "staff"],
            "description": "Type of player",
        },
        "added_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

TEAM_PLAYER_REMOVED_V1 = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "TeamPlayerRemoved v1",
    "description": "Event emitted when a player is removed from a team",
    "required": ["team_id", "player_id", "removed_at"],
    "properties": {
        "team_id": {"type": "string", "format": "uuid"},
        "player_id": {"type": "string", "format": "uuid"},
        "reason": {"type": "string"},
        "removed_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

# Export all modalities schemas
MODALITIES_SCHEMAS = {
    # Nucleo
    "nucleo.created.v1": NUCLEO_CREATED_V1,
    "nucleo.updated.v1": NUCLEO_UPDATED_V1,
    "nucleo.deleted.v1": NUCLEO_DELETED_V1,
    # Course
    "course.created.v1": COURSE_CREATED_V1,
    "course.updated.v1": COURSE_UPDATED_V1,
    "course.deleted.v1": COURSE_DELETED_V1,
    # Modality Type
    "modality_type.created.v1": MODALITY_TYPE_CREATED_V1,
    "modality_type.updated.v1": MODALITY_TYPE_UPDATED_V1,
    "modality_type.deleted.v1": MODALITY_TYPE_DELETED_V1,
    # Modality
    "modality.created.v1": MODALITY_CREATED_V1,
    "modality.updated.v1": MODALITY_UPDATED_V1,
    "modality.deleted.v1": MODALITY_DELETED_V1,
    # Student
    "student.created.v1": STUDENT_CREATED_V1,
    "student.updated.v1": STUDENT_UPDATED_V1,
    "student.deleted.v1": STUDENT_DELETED_V1,
    # Staff
    "staff.created.v1": STAFF_CREATED_V1,
    "staff.updated.v1": STAFF_UPDATED_V1,
    "staff.deleted.v1": STAFF_DELETED_V1,
    # Team
    "team.created.v1": TEAM_CREATED_V1,
    "team.updated.v1": TEAM_UPDATED_V1,
    "team.deleted.v1": TEAM_DELETED_V1,
    "team.player_added.v1": TEAM_PLAYER_ADDED_V1,
    "team.player_removed.v1": TEAM_PLAYER_REMOVED_V1,
}
