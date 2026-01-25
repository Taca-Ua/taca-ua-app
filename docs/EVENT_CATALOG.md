# TACA Event Catalog

Central documentation for all domain events in the TACA system.

**Last Updated**: January 21, 2026
**Schema Version**: 1.0.0

## Overview

This document catalogs all domain events published and consumed across TACA microservices. All events follow the standardized envelope format defined in the [taca-events](../src/shared/taca-events/) schema registry.

## Event Envelope Format

All events use a standard envelope structure:

```json
{
  "event_id": "uuid",
  "event_type": "aggregate.action.v1",
  "event_version": "1.0.0",
  "timestamp": "ISO8601",
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "aggregate_type": "aggregate_name",
  "aggregate_id": "uuid",
  "data": { /* event-specific payload */ },
  "metadata": {
    "published_by": "service-name",
    "source": "api|scheduler|etc"
  }
}
```

## Naming Conventions

- **Event Type**: `{aggregate}.{action}.v{version}`
- **Routing Key**: `{aggregate}.{action}` (version stripped for RabbitMQ)
- **Versions**: Semantic versioning (v1, v2, etc.)

## Events by Service

### Matches Service

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `match.created.v1` | New match created | matches-service | read-model-updater |
| `match.updated.v1` | Match details updated | matches-service | read-model-updater |
| `match.deleted.v1` | Match deleted | matches-service | read-model-updater |
| `match.participant.added.v1` | Participant added to match | matches-service | read-model-updater |
| `match.participant.removed.v1` | Participant removed from match | matches-service | read-model-updater |
| `match.result.updated.v1` | Match scores updated | matches-service | read-model-updater |
| `match.lineup.assigned.v1` | Team lineup assigned | matches-service | read-model-updater |
| `match.comment.added.v1` | Comment added to match | matches-service | read-model-updater |
| `match.comment.deleted.v1` | Comment deleted from match | matches-service | read-model-updater |

### Tournaments Service

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `tournament.created.v1` | New tournament created | tournaments-service | read-model-updater |
| `tournament.updated.v1` | Tournament details updated | tournaments-service | read-model-updater |
| `tournament.deleted.v1` | Tournament deleted | tournaments-service | read-model-updater |
| `tournament.finished.v1` | Tournament completed | tournaments-service | read-model-updater |

### Modalities Service

#### Nucleo Events

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `nucleo.created.v1` | New nucleo created | modalities-service | read-model-updater |
| `nucleo.updated.v1` | Nucleo updated | modalities-service | read-model-updater |
| `nucleo.deleted.v1` | Nucleo deleted | modalities-service | read-model-updater |

#### Course Events

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `course.created.v1` | New course created | modalities-service | read-model-updater |
| `course.updated.v1` | Course updated | modalities-service | read-model-updater |
| `course.deleted.v1` | Course deleted | modalities-service | read-model-updater |

#### Modality Type Events

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `modality_type.created.v1` | New sport type created | modalities-service | read-model-updater |
| `modality_type.updated.v1` | Sport type updated | modalities-service | read-model-updater |
| `modality_type.deleted.v1` | Sport type deleted | modalities-service | read-model-updater |

#### Modality Events

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `modality.created.v1` | New modality created | modalities-service | read-model-updater |
| `modality.updated.v1` | Modality updated | modalities-service | read-model-updater |
| `modality.deleted.v1` | Modality deleted | modalities-service | tournaments-service, read-model-updater |

#### Student Events

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `student.created.v1` | New student registered | modalities-service | read-model-updater |
| `student.updated.v1` | Student info updated | modalities-service | read-model-updater |
| `student.deleted.v1` | Student deleted | modalities-service | read-model-updater |

#### Staff Events

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `staff.created.v1` | New staff member registered | modalities-service | read-model-updater |
| `staff.updated.v1` | Staff info updated | modalities-service | read-model-updater |
| `staff.deleted.v1` | Staff deleted | modalities-service | read-model-updater |

#### Team Events

| Event Type | Description | Publisher | Consumers |
|------------|-------------|-----------|-----------|
| `team.created.v1` | New team created | modalities-service | tournaments-service, read-model-updater |
| `team.updated.v1` | Team details updated | modalities-service | read-model-updater |
| `team.deleted.v1` | Team deleted | modalities-service | tournaments-service, read-model-updater |
| `team.player_added.v1` | Player added to team | modalities-service | read-model-updater |
| `team.player_removed.v1` | Player removed from team | modalities-service | read-model-updater |

## Event Flows

### Match Lifecycle

```
1. Match Created
   modalities-service: tournament.created
   └─> tournaments-service: creates match
       └─> match.created
           └─> read-model-updater: updates read model

2. Match Played
   matches-service: match.result.updated (during game)
   matches-service: match.updated (post-game)
   └─> read-model-updater: updates final standings

3. Match Deleted
   matches-service: match.deleted
   └─> read-model-updater: removes from read model
```

### Tournament Lifecycle

```
1. Tournament Created
   tournaments-service: tournament.created
   └─> read-model-updater: creates tournament view

2. Tournament Finished
   tournaments-service: tournament.finished
   └─> read-model-updater: finalizes results

3. Tournament Deleted
   tournaments-service: tournament.deleted
   └─> read-model-updater: removes tournament
```

### Team Management

```
1. Team Created
   modalities-service: team.created
   ├─> tournaments-service: registers team for tournaments
   └─> read-model-updater: adds to team directory

2. Player Added
   modalities-service: team.player_added
   └─> read-model-updater: updates roster

3. Team Deleted
   modalities-service: team.deleted
   ├─> tournaments-service: removes from active tournaments
   └─> read-model-updater: archives team
```

## Schema Versions

All current events are at version 1.0.0 (v1).

### Version History

- **v1** (2026-01-21): Initial schema release

### Deprecation Policy

When introducing breaking changes:
1. Create new version (e.g., v2)
2. Support both versions for 3 months minimum
3. Announce deprecation with timeline
4. Update all consumers to new version
5. Remove old version after migration period

## Validation

All events are validated using JSON Schema (Draft 7). Schemas are maintained in the [taca-events](../src/shared/taca-events/taca_events/schemas/) package.

To validate an event:

```python
from taca_events import validate_event_data

is_valid, errors = validate_event_data("match.created.v1", event_data)
```

## Schema Registry

Access schemas programmatically:

```python
from taca_events import SchemaRegistry

# Get schema
schema = SchemaRegistry.get_schema("match.created.v1")

# List all events
all_events = SchemaRegistry.list_all_events()

# Get events by service
match_events = SchemaRegistry.get_events_by_service("matches")
```

## References

- [Schema Registry Package](../src/shared/taca-events/)
- [RabbitMQ Messaging](../src/shared/taca-messaging/)
- [Outbox Pattern Documentation](../src/microservices/modalities-service/OUTBOX_PATTERN.md)
