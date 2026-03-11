# TACA Logging

Shared structured logging configuration for TACA services using structlog and Loki.

## Features

- Structured logging with JSON output
- Loki integration for centralized log aggregation
- Consistent logging format across all services
- Support for contextual logging with bind/unbind
- Action-based logging for easy querying

## Usage

### Basic Setup

```python
from taca_logging import configure_logging, get_logger

# Configure logging (do this once at app startup)
configure_logging(
    service_name="my-service",
    log_level="INFO"
)

# Get a logger
logger = get_logger(__name__)

# Log messages
logger.info("service_started")
```

### Action-Based Logging

Use the `action` field for consistent querying across services:

```python
logger.info("request_received", action="list_modalities", method="GET")
logger.info("request_completed", action="list_modalities", status_code=200, count=15)
```

### Contextual Logging

Bind context that persists across multiple log calls:

```python
from structlog import contextvars

# Bind context
contextvars.bind_contextvars(
    user_id="123",
    request_id="abc-def"
)

logger.info("processing_request", action="create_team")
# All subsequent logs will include user_id and request_id

# Clear context when done
contextvars.clear_contextvars()
```

## Querying Logs in Loki

### Find all logs for a specific action
```
{service="modalities-service"} |= "list_modalities"
```

### Find all errors for an action
```
{service="modalities-service"} | json | level="error" | action="create_modality"
```

### Aggregate by action
```
sum by (action) (count_over_time({service="modalities-service"}[1h]))
```
