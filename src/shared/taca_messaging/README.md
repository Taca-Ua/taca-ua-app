# Shared Messaging Module

This directory contains shared utilities for messaging with RabbitMQ across all services in the taca-ua-app project.

## Structure

```
src/shared/
├── __init__.py
└── messaging/
    ├── __init__.py
    └── rabbitmq_service.py
```

## RabbitMQService

A robust RabbitMQ service for managing connections, publishing, and consuming events with a decorator-based pattern similar to FastAPI.

### Features

- **Event-driven architecture**: Publish/Subscribe pattern using RabbitMQ topic exchanges
- **Decorator-based handlers**: Register event handlers using `@event_handler` decorator
- **Wildcard support**: Use `*` and `#` patterns for flexible event routing
- **Connection management**: Automatic reconnection and connection pooling
- **Async/Sync handlers**: Support for both async and synchronous event handlers

### Usage

#### Basic Setup in a Service

```python
import asyncio
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))
from messaging import rabbitmq_service, event_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start RabbitMQ event consumer
    asyncio.create_task(rabbitmq_service.start_consuming(queue_name="my-service-queue"))
    logger.info("Service started")
    yield
    # Disconnect from RabbitMQ on shutdown
    await rabbitmq_service.disconnect()
    logger.info("Service stopped")

app = FastAPI(lifespan=lifespan)
```

#### Registering Event Handlers

```python
from messaging import event_handler

# Handle specific events
@event_handler('match.created')
async def process_match_created(data: dict):
    """Handle match.created events."""
    print(f"Processing match created: {data}")
    match_id = data.get('match_id')
    # Your business logic here

@event_handler('match.updated')
async def process_match_updated(data: dict):
    """Handle match.updated events."""
    print(f"Match {data.get('match_id')} was updated")

# Use wildcards to handle multiple events
@event_handler('match.*')
async def log_all_match_events(data: dict):
    """Log all match-related events."""
    print(f"[AUDIT] Match event occurred: {data}")

# Synchronous handlers are also supported
@event_handler('user.notification')
def send_notification(data: dict):
    """Send a notification (synchronous example)."""
    print(f"Sending notification: {data.get('message')}")
```

#### Publishing Events

```python
from messaging import rabbitmq_service

# Publish an event (pub/sub pattern)
await rabbitmq_service.publish_event(
    'match.created',
    {
        'match_id': 123,
        'team1': 'Team A',
        'team2': 'Team B',
        'scheduled_time': '2025-11-25T18:00:00Z'
    }
)

# Publish directly to a queue (legacy method)
await rabbitmq_service.publish_to_queue(
    'specific-queue',
    {'message': 'Direct queue message'}
)
```

### Event Routing Patterns

The service supports RabbitMQ topic patterns:

- **Exact match**: `match.created` - matches only `match.created`
- **Single word wildcard** (`*`): `match.*` - matches `match.created`, `match.updated`, etc.
- **Multiple words wildcard** (`#`): `match.#` - matches `match.created`, `match.team.updated`, etc.

### Configuration

The service reads configuration from environment variables:

- `RABBITMQ_HOST` - RabbitMQ host (default: `localhost`)
- `RABBITMQ_PORT` - RabbitMQ port (default: `5672`)
- `RABBITMQ_USER` - RabbitMQ username (default: `guest`)
- `RABBITMQ_PASSWORD` - RabbitMQ password (default: `guest`)

### Services Using This Module

All microservices and APIs in the project use this shared module:

- `src/apis/public-api/` - Uses queue: `public-api-queue`
- `src/microservices/matches-service/` - Uses queue: `matches-service-queue`
- `src/microservices/modalities-service/` - Uses queue: `modalities-queue`
- `src/microservices/ranking-service/` - Uses queue: `ranking-queue`
- `src/microservices/read-model-updater/` - Uses queue: `read-model-queue`
- `src/microservices/tournaments-service/` - Uses queue: `tournaments-queue`
