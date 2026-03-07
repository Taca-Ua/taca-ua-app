# RabbitMQ Messaging Service

A simple, decorator-based RabbitMQ service for event-driven microservices with intelligent load balancing.

## Key Features

- **Service-based queue architecture** - Each service has its own queue
- **Cross-service broadcasting** - Same event delivered to all interested services
- **Intra-service load balancing** - Multiple instances of same service share the workload
- **Decorator-based handlers** - FastAPI-like `@event_handler` decorator pattern
- **Topic-based routing** - Support for wildcard patterns (`*` and `#`)
- **Persistent messages** - Messages survive broker restarts

## Architecture

```
Publisher (any service)
    └─> Topic Exchange ("events")
        ├─> Queue: "matches-service.events"
        │   └─> matches-service instance 1 ⎤
        │   └─> matches-service instance 2 ⎦ Load balanced
        │
        └─> Queue: "ranking-service.events"
            └─> ranking-service instance 1 ⎤
            └─> ranking-service instance 2 ⎦ Load balanced
```

**Behavior:**
- ✅ Multiple **different services** → All receive the same event
- ✅ Multiple **instances of same service** → Load balanced (only one instance handles each event)

## Installation

This package is located in `src/shared/taca_messaging`.

## Quick Start

### 1. Create Service Instance

Each service must create its own `RabbitMQService` instance with a unique `service_name`:

```python
from taca_messaging.rabbitmq_service import RabbitMQService

# All instances of "matches-service" will share the same queue
rabbitmq = RabbitMQService(service_name="matches-service")
```

### 2. Define Event Handlers

```python
@rabbitmq.event_handler('match.created')
async def handle_match_created(data: dict):
    print(f"Match created: {data}")
    match_id = data.get('match_id')
    # Your business logic here

@rabbitmq.event_handler('match.*')  # Wildcard: all match events
async def log_match_events(data: dict):
    print(f"[AUDIT] Match event: {data}")
```

### 3. Start Consuming Events

```python
import asyncio

async def main():
    await rabbitmq.start_consuming()
    await asyncio.Future()  # Run forever

asyncio.run(main())
```

### 4. Publish Events

```python
# Any service can publish events
publisher = RabbitMQService(service_name="api-service")

await publisher.publish_event(
    'match.created',
    {'match_id': 123, 'status': 'scheduled'}
)
```

## Configuration

Environment variables:

- `RABBITMQ_HOST` - RabbitMQ server host (default: `localhost`)
- `RABBITMQ_PORT` - RabbitMQ server port (default: `5672`)
- `RABBITMQ_USER` - Username (default: `guest`)
- `RABBITMQ_PASSWORD` - Password (default: `guest`)

## Event Patterns

Supports RabbitMQ topic patterns:

| Pattern | Matches | Example |
|---------|---------|---------|
| `match.created` | Exact match | `match.created` only |
| `match.*` | One word | `match.created`, `match.updated` |
| `match.#` | Zero or more words | `match.created`, `match.team.updated` |

```python
@rabbitmq.event_handler('match.*')
async def handle_any_match_event(data: dict):
    # Handles: match.created, match.updated, match.deleted
    pass
```

## Integration with FastAPI

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from taca_messaging.rabbitmq_service import RabbitMQService

rabbitmq = RabbitMQService(service_name="matches-service")

# Register event handlers
@rabbitmq.event_handler('match.created')
async def handle_match_created(data: dict):
    print(f"Match created: {data}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start consuming events
    await rabbitmq.start_consuming()
    yield
    # Shutdown: Disconnect
    await rabbitmq.disconnect()

app = FastAPI(lifespan=lifespan)

# Publish events from your endpoints
@app.post("/matches")
async def create_match(match_data: dict):
    # ... create match logic ...

    await rabbitmq.publish_event('match.created', {
        'match_id': match_data['id'],
        'teams': match_data['teams']
    })

    return {"status": "created"}
```

## Example: Multiple Services

```python
# Service 1: Matches Service
matches_rabbitmq = RabbitMQService(service_name="matches-service")

@matches_rabbitmq.event_handler("match.created")
async def matches_handler(data: dict):
    print(f"[matches-service] Processing: {data}")

# Service 2: Ranking Service
ranking_rabbitmq = RabbitMQService(service_name="ranking-service")

@ranking_rabbitmq.event_handler("match.created")
async def ranking_handler(data: dict):
    print(f"[ranking-service] Updating rankings: {data}")

# Start both
await matches_rabbitmq.start_consuming()
await ranking_rabbitmq.start_consuming()

# Publish event
publisher = RabbitMQService(service_name="api")
await publisher.publish_event("match.created", {"match_id": 123})

# Result: BOTH services receive the event!
# [matches-service] Processing: {'match_id': 123}
# [ranking-service] Updating rankings: {'match_id': 123}
```

## Load Balancing Behavior

### Scenario 1: Same Service, Multiple Instances
```python
# Instance 1 of matches-service
rabbitmq1 = RabbitMQService(service_name="matches-service")
await rabbitmq1.start_consuming()

# Instance 2 of matches-service (same service_name)
rabbitmq2 = RabbitMQService(service_name="matches-service")
await rabbitmq2.start_consuming()

# Publish 10 events
for i in range(10):
    await publisher.publish_event("match.created", {"id": i})

# Result: Events are load-balanced between instance 1 and 2
# Only ONE instance handles each event
```

### Scenario 2: Different Services
```python
# Matches service
matches = RabbitMQService(service_name="matches-service")
await matches.start_consuming()

# Ranking service (different service_name)
ranking = RabbitMQService(service_name="ranking-service")
await ranking.start_consuming()

# Publish 1 event
await publisher.publish_event("match.created", {"id": 1})

# Result: BOTH services receive the event
# No load balancing between different services
```

## Best Practices

1. **Use descriptive service names**: `"matches-service"`, `"ranking-service"`, `"notifications-service"`
2. **Use dotted event names**: `"match.created"`, `"tournament.started"`, `"user.registered"`
3. **Handle errors gracefully**: Wrap handler logic in try-except
4. **Keep handlers fast**: For slow operations, dispatch to background tasks
5. **Use wildcards sparingly**: Prefer specific event names for clarity

## API Reference

### `RabbitMQService(service_name, host=None, port=None, user=None, password=None, exchange_name="events")`

Create a new RabbitMQ service instance.

**Parameters:**
- `service_name` (str, required): Unique name for this service
- `host` (str): RabbitMQ host
- `port` (int): RabbitMQ port
- `user` (str): Username
- `password` (str): Password
- `exchange_name` (str): Exchange name (default: `"events"`)

### `@rabbitmq.event_handler(event_pattern)`

Decorator to register an event handler.

**Parameters:**
- `event_pattern` (str): Event name or pattern (supports `*` and `#` wildcards)

### `await rabbitmq.publish_event(event_name, data)`

Publish an event to the exchange.

**Parameters:**
- `event_name` (str): Event routing key
- `data` (dict): Event payload (must be JSON-serializable)

### `await rabbitmq.start_consuming()`

Start consuming events. Blocks until stopped.

### `await rabbitmq.disconnect()`

Close the RabbitMQ connection.
