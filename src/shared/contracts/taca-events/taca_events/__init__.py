"""
TACA Events

Typed Pydantic event schemas for the TACA system.

    from taca_events.pydantic_schemas import (
        EventRegistry,
        MatchCreatedV1, MatchCreatedData,
        ...
    )
"""

from .builder import EventBuilder
from .pydantic_schemas import matches, modalities, tournaments
from .types import EventType, RoutingKeys

__all__ = [
    "EventBuilder",
    "EventType",
    "RoutingKeys",
    "matches",
    "modalities",
    "tournaments",
]

__version__ = "1.0.0"
