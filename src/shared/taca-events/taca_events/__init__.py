"""
TACA Events Schema Registry

Centralized event schema definitions and validation for the TACA system.
"""

from .builder import EventBuilder
from .registry import SchemaRegistry
from .types import EventType, RoutingKeys
from .validator import validate_event, validate_event_data

__all__ = [
    "EventBuilder",
    "EventType",
    "RoutingKeys",
    "SchemaRegistry",
    "validate_event",
    "validate_event_data",
]

__version__ = "1.0.0"
