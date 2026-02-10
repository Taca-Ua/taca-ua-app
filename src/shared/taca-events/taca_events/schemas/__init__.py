"""Event schemas organized by service."""

from .base import BASE_EVENT_ENVELOPE_SCHEMA
from .matches import MATCH_SCHEMAS
from .modalities import MODALITIES_SCHEMAS
from .tournaments import TOURNAMENT_SCHEMAS

# Combine all schemas
ALL_SCHEMAS = {
    **MATCH_SCHEMAS,
    **MODALITIES_SCHEMAS,
    **TOURNAMENT_SCHEMAS,
}

__all__ = [
    "BASE_EVENT_ENVELOPE_SCHEMA",
    "ALL_SCHEMAS",
    "MATCH_SCHEMAS",
    "MODALITIES_SCHEMAS",
    "TOURNAMENT_SCHEMAS",
]
