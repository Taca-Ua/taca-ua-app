"""
TACA Events Schema Registry

Centralized event schema definitions and validation for the TACA system.

New typed Pydantic schemas are available via ``taca_events.pydantic_schemas``:

    from taca_events.pydantic_schemas import (
        EventRegistry,
        MatchCreatedV1, MatchCreatedData,
        ...
    )
"""

from .builder import EventBuilder
from .registry import SchemaRegistry
from .types import EventType, RoutingKeys
from .validator import validate_event, validate_event_data

__all__ = [
    "EventBuilder",
    "SchemaRegistry",
    "EventType",
    "RoutingKeys",
    "validate_event",
    "validate_event_data",
]

__version__ = "1.0.0"
