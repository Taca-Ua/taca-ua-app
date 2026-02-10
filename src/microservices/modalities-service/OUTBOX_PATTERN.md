# Modalities Service - Outbox Pattern Implementation

## Overview

The Modalities Service now implements the **Transactional Outbox Pattern** for reliable event publishing. This ensures that domain events are persisted atomically with business data and published reliably to RabbitMQ.

## Architecture

### Components

1. **OutboxEvent Model** ([models.py](app/models.py))
   - Stores events in the database before publishing
   - Fields: event_type, aggregate_type, aggregate_id, payload, published, retry_count
   - Indexed for efficient querying of unpublished events

2. **OutboxPublisher Service** ([outbox_publisher.py](app/outbox_publisher.py))
   - Background task that polls for unpublished events
   - Publishes events to RabbitMQ
   - Handles retries and error tracking
   - Configurable poll interval (default: 5 seconds)
   - Batch processing (default: 100 events per batch)
   - Max retries (default: 3 attempts)

3. **Event Helpers** ([event_helpers.py](app/event_helpers.py))
   - Convenience functions for emitting events
   - Event type constants for consistency
   - Simple API: `emit_event(db, event_type, aggregate_type, aggregate_id, data)`

4. **Updated Routes** ([routes.py](app/routes.py))
   - All create/update/delete operations emit events
   - Events saved in same transaction as business data
   - Atomic guarantees using `db.flush()` before event creation

## Event Types

The service emits the following domain events:

### Nucleo Events
- `nucleo.created` - When a nucleo is created
- `nucleo.updated` - When a nucleo is updated
- `nucleo.deleted` - When a nucleo is deleted

### Course Events
- `course.created` - When a course is created
- `course.updated` - When a course is updated
- `course.deleted` - When a course is deleted

### Modality Type Events
- `modality_type.created` - When a modality type is created
- `modality_type.updated` - When a modality type is updated
- `modality_type.deleted` - When a modality type is deleted

### Modality Events
- `modality.created` - When a modality is created
- `modality.updated` - When a modality is updated
- `modality.deleted` - When a modality is deleted

### Student Events
- `student.created` - When a student is created
- `student.updated` - When a student is updated
- `student.deleted` - When a student is deleted

### Staff Events
- `staff.created` - When a staff member is created
- `staff.updated` - When a staff member is updated
- `staff.deleted` - When a staff member is deleted

### Team Events
- `team.created` - When a team is created
- `team.updated` - When a team is updated
- `team.deleted` - When a team is deleted
- `team.player_added` - When a player is added to a team
- `team.player_removed` - When a player is removed from a team

## How It Works

### 1. Event Creation
When a domain operation occurs (e.g., creating a student):

```python
# Create the student
student = Student(...)
db.add(student)
db.flush()  # Get ID without committing

# Save event to outbox (same transaction)
emit_event(
    db=db,
    event_type=EventTypes.STUDENT_CREATED,
    aggregate_type="student",
    aggregate_id=student.id,
    data=student.to_dict(),
)

# Commit both student and event atomically
db.commit()
```

### 2. Event Publishing
The `OutboxPublisher` runs as a background task:

```python
# Polls every 5 seconds
while running:
    # Fetch unpublished events
    events = query(OutboxEvent).filter(published=False).limit(100)

    # Publish each event
    for event in events:
        await rabbitmq_service.publish_event(event.event_type, event.payload)
        event.published = True
        event.published_at = now()
        db.commit()

    await sleep(5)
```

### 3. Retry Logic
- Failed events increment `retry_count`
- `last_error` field stores error details
- Events stop retrying after `max_retries` (default: 3)
- Manual intervention needed for permanently failed events

## Benefits

1. **Atomicity**: Events and data changes are saved in same transaction
2. **Reliability**: Events are never lost, even if RabbitMQ is down
3. **Auditability**: All events stored in database with timestamps
4. **Replay Capability**: Can replay events from outbox table
5. **Debugging**: Easy to inspect failed events and retry manually
6. **Ordering**: Events processed in creation order
7. **At-least-once delivery**: Events guaranteed to be published at least once

## Database Migration

Run the migration to create the outbox table:

```bash
cd src/microservices/modalities-service
alembic upgrade head
```

This creates the `outbox_event` table with appropriate indexes.

## Configuration

The OutboxPublisher can be configured in [outbox_publisher.py](app/outbox_publisher.py):

```python
outbox_publisher = OutboxPublisher(
    poll_interval=5,      # seconds between polling
    batch_size=100,       # max events per batch
    max_retries=3,        # max retry attempts
)
```

## Monitoring

### Check Unpublished Events

```sql
SELECT COUNT(*) FROM outbox_event WHERE published = FALSE;
```

### Check Failed Events

```sql
SELECT * FROM outbox_event
WHERE published = FALSE
  AND retry_count >= 3
ORDER BY created_at;
```

### Event Distribution by Type

```sql
SELECT event_type, COUNT(*)
FROM outbox_event
GROUP BY event_type
ORDER BY COUNT(*) DESC;
```

### Publishing Lag

```sql
SELECT
    MIN(created_at) as oldest_unpublished,
    NOW() - MIN(created_at) as lag
FROM outbox_event
WHERE published = FALSE;
```

## Manual Event Replay

To manually replay events (e.g., after fixing RabbitMQ):

```sql
-- Reset published flag for failed events
UPDATE outbox_event
SET published = FALSE, retry_count = 0, last_error = NULL
WHERE retry_count >= 3;
```

The OutboxPublisher will automatically pick them up in the next poll.

## Integration with Other Services

Other microservices should:

1. **Subscribe to relevant events**:
```python
@rabbitmq_service.event_handler('student.created')
async def handle_student_created(data: dict):
    # Update read model, etc.
    pass
```

2. **Handle duplicate events** (at-least-once delivery):
   - Use idempotency keys
   - Check if already processed
   - Design operations to be idempotent

3. **Handle out-of-order events** (rare but possible):
   - Use version numbers
   - Use timestamps
   - Design for eventual consistency

## Testing

### Unit Tests
Test event emission without actually publishing:
```python
def test_create_student_emits_event(db):
    student = create_student(...)
    events = db.query(OutboxEvent).filter(
        OutboxEvent.event_type == EventTypes.STUDENT_CREATED
    ).all()
    assert len(events) == 1
```

### Integration Tests
Test end-to-end event flow:
```python
async def test_event_published_to_rabbitmq():
    # Create entity
    student = create_student(...)

    # Wait for OutboxPublisher
    await asyncio.sleep(6)

    # Check event was published
    event = db.query(OutboxEvent).first()
    assert event.published == True
```

## Future Enhancements

1. **Dead Letter Queue**: Move permanently failed events to separate table
2. **Event Versioning**: Support schema evolution
3. **Batch Publishing**: Publish multiple events in single RabbitMQ transaction
4. **Metrics**: Export Prometheus metrics for monitoring
5. **Admin API**: Endpoints to manage failed events
6. **Event Filtering**: Allow consumers to filter events by criteria
