# TACA Structured Logging with Loki

This document describes the structured logging setup for the TACA application using structlog and Loki.

## Overview

All microservices and APIs now use **structlog** for structured logging, with logs aggregated in **Loki** for centralized querying and analysis.

## Architecture

```
┌─────────────────┐
│  Microservices  │
│  & APIs         │
│  (structlog)    │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │  Loki  │
    └────────┘
         │
         ▼
    ┌────────┐
    │ Grafana│
    └────────┘
```

## Key Features

### 1. **Action-Based Logging**
Every API endpoint automatically logs with an `action` field that describes the operation:
- `list_modalities` - List all modalities
- `create_modality` - Create a new modality
- `get_modality` - Get a specific modality
- `update_modality` - Update a modality
- `delete_modality` - Delete a modality

### 2. **Request Context**
Each request automatically includes:
- `request_id` - Unique identifier for the request
- `method` - HTTP method (GET, POST, PUT, DELETE)
- `path` - API endpoint path
- `action` - Operation being performed
- `status_code` - HTTP response code
- `duration_ms` - Request duration in milliseconds

### 3. **Structured Fields**
Logs include structured data that can be queried:
- Entity IDs (e.g., `modality_id`, `student_id`)
- Error details (e.g., `error`, `error_message`)
- Business events (e.g., `entity_created`, `entity_updated`)

## Components

### Shared Logging Package: `taca-logging`

Located at: `src/shared/taca-logging/`

**Main Functions:**
- `configure_logging(service_name, log_level)` - Configure structured logging for a service
- `get_logger(name)` - Get a structlog logger instance
- `StructlogMiddleware` - FastAPI middleware for automatic request/response logging

### FastAPI Services

**Services:**
- `modalities-service`
- `matches-service`
- `tournaments-service`
- `ranking-service`
- `read-model-updater`
- `public-api`

**Logging Setup:**
1. Import and configure logging in `app/logger.py` or `app/main.py`
2. Add `StructlogMiddleware` to FastAPI app
3. All requests are automatically logged with action identifiers

**Example:**
```python
from taca_logging import StructlogMiddleware, configure_logging, get_logger

configure_logging(service_name="my-service", log_level="INFO")
logger = get_logger("my-service")

app = FastAPI()
app.add_middleware(StructlogMiddleware)

# All routes automatically logged
@app.get("/items")
def list_items():
    return {"items": []}
```

### Django Service (competition-api)

**Logging Setup:**
1. Configure logging in `competition_api/settings.py`
2. Add `StructlogMiddleware` to Django middleware
3. Use `@log_action` decorator on view methods

**Example:**
```python
from admin_api.logging_decorators import log_action

class ModalityListCreateView(APIView):
    @log_action("list_modalities")
    def get(self, request):
        ...

    @log_action("create_modality")
    def post(self, request):
        ...
```

## Querying Logs in Loki

### Basic Queries

**Find all logs for a service:**
```logql
{service="modalities-service"}
```

**Find all logs for a specific action:**
```logql
{service="modalities-service"} | json | action="list_modalities"
```

**Find all errors:**
```logql
{service="modalities-service"} | json | level="error"
```

**Find logs for a specific request:**
```logql
{service="modalities-service"} | json | request_id="abc-def-123"
```

### Advanced Queries

**Count requests by action:**
```logql
sum by (action) (count_over_time({service="modalities-service"} | json | action != "" [1h]))
```

**Average request duration by action:**
```logql
avg by (action) (avg_over_time({service="modalities-service"} | json | duration_ms != "" | unwrap duration_ms [5m]))
```

**Find slow requests (>1000ms):**
```logql
{service="modalities-service"} | json | duration_ms > 1000
```

**Error rate by action:**
```logql
sum by (action) (rate({service="modalities-service"} | json | level="error" [5m]))
```

**Find all operations on a specific entity:**
```logql
{service="modalities-service"} | json | modality_id="550e8400-e29b-41d4-a716-446655440000"
```

### Cross-Service Queries

**Find all operations across services for a user:**
```logql
{service=~".*-service|.*-api"} | json | user_id="123"
```

**Find all create operations across all services:**
```logql
{service=~".*-service|.*-api"} | json | action=~"create_.*"
```

## Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical failures

## Best Practices

### 1. Use Action Names Consistently

Follow the naming pattern:
- `list_{resource}` - List resources
- `get_{resource}` - Get a single resource
- `create_{resource}` - Create a resource
- `update_{resource}` - Update a resource
- `delete_{resource}` - Delete a resource

### 2. Log Business Events

In addition to automatic request logging, log important business events:

```python
logger.info("entity_created",
    entity_type="modality",
    entity_id=str(modality.id),
    name=modality.name
)
```

### 3. Log Errors with Context

```python
logger.error("operation_failed",
    action="create_modality",
    error="validation_error",
    details=str(e)
)
```

### 4. Use Structured Fields

Always use structured fields instead of string formatting:

**Good:**
```python
logger.info("user_logged_in", user_id=user.id, username=user.name)
```

**Bad:**
```python
logger.info(f"User {user.id} logged in")
```

## Environment Variables

Configure logging behavior with environment variables:

- `LOG_LEVEL` - Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Default: `INFO`

## Grafana Dashboards

Access Grafana at: `http://localhost:3000`

**Suggested Dashboards:**
1. **Request Overview** - Request count, error rate, avg duration by service
2. **Action Metrics** - Metrics grouped by action (list, create, update, delete)
3. **Error Analysis** - Error types, frequency, affected endpoints
4. **Performance** - Request duration percentiles, slow queries

## Troubleshooting

### Logs not appearing in Loki

1. Check service is running: `docker ps`
2. Check Loki is reachable: `curl http://localhost:3100/ready`
3. Check service logs: `docker logs <service-name>`
4. Verify logging configuration in service

### Queries returning no results

1. Verify time range in Grafana
2. Check label names: `{service="modalities-service"}` (not `application`)
3. Use `| json` to parse JSON logs before filtering fields
4. Check log level filter

### Missing structured fields

1. Ensure `| json` is in query
2. Verify field names match exactly (case-sensitive)
3. Check logs are being sent as JSON

## Migration Notes

### For Developers

When adding new endpoints or views:

**FastAPI:** No action needed - middleware handles logging automatically

**Django:** Add `@log_action("action_name")` decorator to view methods

### Testing Locally

```bash
# Start services
docker-compose up -d

# Generate some logs
curl http://localhost:8001/api/admin/modalities

# Query logs
# Open Grafana: http://localhost:3000
# Navigate to Explore
# Select Loki data source
# Run query: {service="competition-api"}
```

## Support

For questions or issues:
1. Check this documentation
2. Review `src/shared/taca-logging/README.md`
3. Check `src/apis/competiotion-api/LOGGING_GUIDE.md` for Django-specific guidance
