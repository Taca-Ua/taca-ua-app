# TACA Events Schema Registry

Central schema registry for all domain events in the TACA system.

## Overview

This package provides:
- **JSON Schema definitions** for all domain events
- **Event validation** utilities
- **Event type catalog** with versioning
- **Standard event envelope** format
- **Type hints** for Python

## Installation

```bash
pip install -e src/shared/taca-events
```

## Usage

### Publishing Events

```python
from taca_events import EventBuilder, EventType

# Create and validate an event
event = EventBuilder.create(
    event_type=EventType.MATCH_CREATED,
    data={
        "match_id": "123e4567-e89b-12d3-a456-426614174000",
        "tournament_id": "123e4567-e89b-12d3-a456-426614174001",
        "team_home_id": "123e4567-e89b-12d3-a456-426614174002",
        "team_away_id": "123e4567-e89b-12d3-a456-426614174003",
        "start_time": "2026-01-21T18:00:00Z",
        "created_at": "2026-01-21T12:00:00Z"
    },
    correlation_id="req-12345",
)

# Event is automatically validated against schema
await rabbitmq.publish_event(event.event_type, event.to_dict())
```

### Consuming Events

```python
from taca_events import validate_event

@rabbitmq.event_handler("match.created")
async def handle_match_created(data: dict):
    # Validate incoming event
    is_valid, errors = validate_event("match.created.v1", data)
    if not is_valid:
        logger.error(f"Invalid event: {errors}")
        return

    # Process event
    match_id = data["data"]["match_id"]
```

## Event Envelope Format

All events follow a standard envelope:

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "match.created",
  "event_version": "1.0.0",
  "timestamp": "2026-01-21T12:00:00.000Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440001",
  "causation_id": "550e8400-e29b-41d4-a716-446655440002",
  "aggregate_type": "match",
  "aggregate_id": "550e8400-e29b-41d4-a716-446655440003",
  "data": {
    // Event-specific payload
  },
  "metadata": {
    "published_by": "matches-service",
    "source": "api"
  }
}
```

## Event Catalog

### Modalities Service Events
- `nucleo.created.v1`, `nucleo.updated.v1`, `nucleo.deleted.v1`
- `course.created.v1`, `course.updated.v1`, `course.deleted.v1`
- `modality_type.created.v1`, `modality_type.updated.v1`, `modality_type.deleted.v1`
- `modality.created.v1`, `modality.updated.v1`, `modality.deleted.v1`
- `student.created.v1`, `student.updated.v1`, `student.deleted.v1`
- `staff.created.v1`, `staff.updated.v1`, `staff.deleted.v1`
- `team.created.v1`, `team.updated.v1`, `team.deleted.v1`
- `team.player_added.v1`, `team.player_removed.v1`

### Tournaments Service Events
- `tournament.created.v1`
- `tournament.updated.v1`
- `tournament.deleted.v1`
- `tournament.finished.v1`

### Matches Service Events
- `match.created.v1`, `match.updated.v1`, `match.deleted.v1`
- `match.finished.v1`
- `match.participant.added.v1`, `match.participant.removed.v1`
- `match.result.updated.v1`
- `match.lineup.assigned.v1`
- `match.comment.added.v1`, `match.comment.deleted.v1`

## Schema Versioning

Event schemas use semantic versioning:
- **Major**: Breaking changes (remove/rename fields)
- **Minor**: Backward-compatible additions (new optional fields)
- **Patch**: Documentation/clarification only

When introducing breaking changes:
1. Create new schema version (e.g., `match.created.v2`)
2. Support both versions for migration period
3. Update consumers to handle new version
4. Deprecate old version
5. Remove old version after migration complete

## Validation

Schemas are validated using JSON Schema Draft 7.

```python
from taca_events import SchemaRegistry

# Get schema
schema = SchemaRegistry.get_schema("match.created.v1")

# Validate data
from taca_events.validator import validate_event_data

is_valid, errors = validate_event_data("match.created.v1", event_data)
```
