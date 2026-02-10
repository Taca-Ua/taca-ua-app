"""
Event validation utilities.
"""

from typing import Tuple

import jsonschema
from jsonschema import Draft7Validator

from .registry import SchemaRegistry
from .schemas import BASE_EVENT_ENVELOPE_SCHEMA


def validate_event_data(event_type: str, data: dict) -> Tuple[bool, list]:
    """
    Validate event data against its schema (without envelope).

    Args:
        event_type: Full event type (e.g., 'match.created.v1')
        data: Event payload data (not the full envelope)

    Returns:
        Tuple of (is_valid, errors)
        - is_valid: Boolean indicating if validation passed
        - errors: List of validation error messages
    """
    schema = SchemaRegistry.get_schema(event_type)

    if not schema:
        return False, [f"No schema found for event type: {event_type}"]

    validator = Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(data):
        # Format error message with path
        path = ".".join(str(p) for p in error.path) if error.path else "root"
        errors.append(f"{path}: {error.message}")

    return len(errors) == 0, errors


def validate_event(event_type: str, event: dict) -> Tuple[bool, list]:
    """
    Validate a complete event including envelope and data.

    Args:
        event_type: Full event type (e.g., 'match.created.v1')
        event: Complete event dict with envelope

    Returns:
        Tuple of (is_valid, errors)
    """
    all_errors = []

    # Validate envelope structure
    envelope_validator = Draft7Validator(BASE_EVENT_ENVELOPE_SCHEMA)
    for error in envelope_validator.iter_errors(event):
        path = ".".join(str(p) for p in error.path) if error.path else "root"
        all_errors.append(f"Envelope {path}: {error.message}")

    # Validate event data
    if "data" in event:
        data_valid, data_errors = validate_event_data(event_type, event["data"])
        if not data_valid:
            all_errors.extend([f"Data {err}" for err in data_errors])

    return len(all_errors) == 0, all_errors


def validate_event_schema(schema: dict) -> Tuple[bool, list]:
    """
    Validate that a schema itself is valid JSON Schema.

    Args:
        schema: JSON schema dict

    Returns:
        Tuple of (is_valid, errors)
    """
    try:
        Draft7Validator.check_schema(schema)
        return True, []
    except jsonschema.SchemaError as e:
        return False, [str(e)]
