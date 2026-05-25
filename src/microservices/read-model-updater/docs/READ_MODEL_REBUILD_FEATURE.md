# Read Model Updater - Rebuild / Snapshot Sync Feature

## Overview

The **Rebuild/Snapshot Sync** feature enables the Read Model Updater microservice to completely rebuild all projection tables from snapshots provided by domain services. This is essential for:

- **Recovery**: Rebuild projections after data corruption or loss
- **Initial Population**: Bootstrap projections when starting fresh
- **Consistency Fixes**: Resync projections with source-of-truth data
- **Testing**: Reset projections to a known state

## Architecture

### Key Architectural Decisions

1. **Single Orchestrator**:
   - Only the Read Model Updater orchestrates rebuild
   - API Gateway must NOT orchestrate rebuild logic
   - Domain services must NOT call each other

2. **Service Communication**:
   - Services communicate via Docker service name DNS resolution
   - No hardcoded IP addresses
   - All URLs come from environment variables

3. **Snapshot Endpoints**:
   - Each domain service exposes `GET /internal/snapshot`
   - Endpoints are internal-only (not exposed via API Gateway)
   - Accessible within Docker network only

4. **Event Consumption**:
   - Events are paused during rebuild
   - Messages buffer in RabbitMQ queue
   - Resume automatically after rebuild completes

5. **Data Consistency**:
   - All projection tables are cleared before rebuild
   - Data is inserted in correct dependency order
   - Transactional operations with rollback on failure

## Components

### 1. Configuration (`config.py`)

Centralized configuration for:
- Database connection
- RabbitMQ connection
- Domain service URLs (via environment variables)
- Security tokens
- Snapshot fetch timeout and retries

**Key Environment Variables**:
```env
MATCHES_SERVICE_URL=http://matches-service:8000
TOURNAMENT_SERVICE_URL=http://tournaments-service:8000
MODALITIES_SERVICE_URL=http://modalities-service:8000
RANKING_SERVICE_URL=http://ranking-service:8000
INTERNAL_API_TOKEN=your-secure-token-here
SNAPSHOT_REQUEST_TIMEOUT=30
SNAPSHOT_MAX_RETRIES=3
```

### 2. Data Transfer Objects (`dto.py`)

Type-safe DTOs for:
- `MatchesSnapshot`: Match, participants, results, lineups, comments
- `TournamentSnapshot`: Tournaments and competitors
- `ModalitiesSnapshot`: Modalities, teams, students, staff, etc.
- `RankingSnapshot`: Ranking data
- `CompleteSnapshot`: Aggregated snapshot from all services
- `RebuildResult`: Result metadata (success, records processed, errors)

### 3. Snapshot HTTP Client (`snapshot_client.py`)

Responsible for:
- Making HTTP requests to domain service snapshot endpoints
- Handling timeouts and retries
- Transforming raw HTTP responses into structured DTOs
- Fail-fast error handling

**Key Features**:
- Uses `httpx` for async HTTP requests
- Configurable timeout (default 30 seconds)
- Configurable retries (default 3 attempts)
- Returns `None` for unavailable services (404)
- Raises `SnapshotFetchError` on failures

### 4. Projection Repository (`projection_repository.py`)

Manages database operations:
- `clear_all_projections()`: Safely deletes all projection data
- `rebuild_from_snapshot()`: Populates projections from snapshot
- `reset_sequences()`: Ensures ID sequences are correct

**Clearing Order** (respects foreign keys):
1. Match comments, lineups, results, participants
2. Matches
3. Tournament competitors
4. Tournaments
5. Team players
6. Teams
7. Students and staff
8. Modalities and modality types
9. Courses and nucleos

**Rebuild Order** (respects dependencies):
1. Base reference data (nucleos, courses, modality types, etc.)
2. Modalities, students, staff, teams
3. Tournaments and competitors
4. Matches and related data

### 5. Rebuild Service (`rebuild_service.py`)

Core orchestration logic:
- `execute_rebuild()`: Main entry point for rebuild process
- `pause_event_consumption()`: Stops processing events
- `clear_projections()`: Clears all projection tables
- `fetch_snapshots()`: Gets data from all domain services
- `rebuild_projections()`: Populates projections
- `resume_event_consumption()`: Restarts event processing

**Process Flow**:
```
1. Pause event consumption
2. Clear all projection tables
3. Fetch snapshots from domain services
4. Rebuild projections from snapshots
5. Resume event consumption
```

If any step fails, it attempts to resume event consumption before propagating the error.

### 6. Pausable RabbitMQ Service (`events.py`)

Extended RabbitMQ service with pause/resume capabilities:
- `pause_consumption()`: Cancels consumers (messages queue in RabbitMQ)
- `resume_consumption()`: Re-starts consuming messages
- `is_paused()`: Check current pause state

### 7. Rebuild Controller (`rebuild_controller.py`)

HTTP endpoints for rebuild operations:

#### `POST /internal/rebuild`
Triggers projection rebuild from domain service snapshots.

**Authentication**: Requires `X-INTERNAL-TOKEN` header

**Request**:
```bash
curl -X POST http://read-model-updater:8000/internal/rebuild \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

**Response** (success):
```json
{
  "success": true,
  "message": "Rebuild completed successfully",
  "records_processed": 1523,
  "duration_seconds": 4.52
}
```

**Response** (failure):
```json
{
  "success": false,
  "message": "Rebuild failed",
  "errors": ["Failed to fetch snapshots: Connection timeout"],
  "duration_seconds": 2.13
}
```

#### `GET /internal/rebuild/status`
Get current rebuild status and projection statistics.

**Response**:
```json
{
  "success": true,
  "status": {
    "projections": {
      "matches": 45,
      "tournaments": 8,
      "teams": 32,
      "students": 487,
      "modalities": 12
    },
    "event_consumption_paused": false
  }
}
```

#### `POST /internal/rebuild/pause`
Manually pause event consumption (useful for maintenance).

#### `POST /internal/rebuild/resume`
Manually resume event consumption.

## Usage

### Prerequisites

1. All domain services must implement `/internal/snapshot` endpoints
2. Environment variables must be configured in `docker-compose.yml`
3. Internal API token must be set (not using default)

### Triggering a Rebuild

**Option 1: Using curl**
```bash
curl -X POST http://localhost:8000/internal/rebuild \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

**Option 2: From another service (Python)**
```python
import httpx

async def trigger_rebuild():
    headers = {"X-INTERNAL-TOKEN": "your-token-here"}
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(
            "http://read-model-updater:8000/internal/rebuild",
            headers=headers
        )
        result = response.json()
        print(result)
```

**Option 3: From within Docker network**
```bash
docker exec -it <container-id> curl -X POST http://read-model-updater:8000/internal/rebuild \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

### Checking Rebuild Status

```bash
curl http://read-model-updater:8000/internal/rebuild/status \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

### Manual Pause/Resume

**Pause**:
```bash
curl -X POST http://read-model-updater:8000/internal/rebuild/pause \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

**Resume**:
```bash
curl -X POST http://read-model-updater:8000/internal/rebuild/resume \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

## Domain Service Implementation

Each domain service needs to implement the snapshot endpoint. Example:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/internal", tags=["internal"])

@router.get("/snapshot")
def get_snapshot():
    """
    Return complete snapshot of service data.

    This endpoint should be internal-only and not exposed via API Gateway.
    """
    # Fetch all data from domain service database
    matches = get_all_matches()
    participants = get_all_participants()
    results = get_all_results()
    # ... more data

    return {
        "matches": [match.dict() for match in matches],
        "participants": [p.dict() for p in participants],
        "results": [r.dict() for r in results],
        # ... more data
    }
```

**Important**:
- Return data as dictionaries (not model instances)
- Include all fields needed for rebuilding projections
- Handle pagination if dataset is large
- Consider adding metadata (timestamp, version, record count)

## Security Considerations

1. **Internal API Token**:
   - Never use the default token in production
   - Set `INTERNAL_API_TOKEN` environment variable
   - Use a strong, randomly generated token

2. **Network Isolation**:
   - Rebuild endpoints should NOT be exposed via API Gateway
   - Only accessible within Docker network
   - Consider using internal network in Docker Compose

3. **Authentication**:
   - All rebuild endpoints require `X-INTERNAL-TOKEN` header
   - Invalid tokens return 401 Unauthorized

4. **Audit Logging**:
   - All rebuild operations are logged
   - Includes who triggered rebuild, timestamp, result
   - Check logs for unauthorized access attempts

## Error Handling

### Snapshot Fetch Failures

If any domain service fails to provide a snapshot:
- Rebuild process fails immediately (fail-fast)
- Event consumption is resumed
- Error is logged with service name and details
- Returns 500 with error message

### Database Failures

If projection clearing or rebuilding fails:
- Database transaction is rolled back
- No partial data remains
- Event consumption is resumed
- Error is logged with details

### Timeout Handling

If snapshot fetching times out:
- Retries up to `SNAPSHOT_MAX_RETRIES` times
- If all retries fail, rebuild fails
- Timeout is configurable via `SNAPSHOT_REQUEST_TIMEOUT`

## Performance Considerations

1. **Duration**:
   - Rebuild can take several seconds to minutes depending on data size
   - Consider running during low-traffic periods

2. **Event Buffering**:
   - Events are buffered in RabbitMQ during rebuild
   - Ensure RabbitMQ has sufficient memory
   - Consider pausing event publishers if possible

3. **Database Load**:
   - Clearing and inserting can be resource-intensive
   - Use database connection pooling
   - Monitor database performance during rebuild

4. **HTTP Timeouts**:
   - Default timeout is 30 seconds per service
   - Increase if services have large datasets
   - Consider pagination for very large snapshots

## Monitoring

### Structured Logging

All operations are logged with structured logging (via `taca_logging`):

- `rebuild_started`: Rebuild process initiated
- `rebuild_step`: Each step of rebuild process
- `snapshot_fetch_started`: Fetching snapshot from service
- `snapshot_fetch_success`: Snapshot fetched successfully
- `projection_clear_success`: Projections cleared
- `projection_rebuild_success`: Projections rebuilt
- `rebuild_completed`: Rebuild finished successfully
- `rebuild_failed`: Rebuild failed with error

### Metrics

Monitor these Prometheus metrics:
- Rebuild duration
- Snapshot fetch duration per service
- Projection rebuild duration
- Number of records processed
- Error rates

### Health Checks

After rebuild, verify:
- All projection tables have data
- Record counts match expectations
- Foreign key relationships are intact
- Event consumption is resumed

## Testing

### Unit Tests

Test each component independently:
- Snapshot client with mocked HTTP responses
- Projection repository with test database
- Rebuild service with mocked dependencies

### Integration Tests

Test end-to-end rebuild:
1. Start all services
2. Populate domain services with test data
3. Trigger rebuild
4. Verify projection data matches source data

### Manual Testing

```bash
# 1. Clear existing projections
curl -X POST http://localhost:8000/internal/rebuild \
  -H "X-INTERNAL-TOKEN: test-token"

# 2. Check status
curl http://localhost:8000/internal/rebuild/status \
  -H "X-INTERNAL-TOKEN: test-token"

# 3. Verify data in database
docker exec -it <postgres-container> psql -U user -d taca_db
SELECT COUNT(*) FROM public_read.matches;
SELECT COUNT(*) FROM public_read.tournaments;
```

## Troubleshooting

### "Failed to fetch snapshots"

**Cause**: Domain service is not responding or snapshot endpoint doesn't exist

**Solution**:
- Check if domain service is running: `docker ps`
- Check service logs: `docker logs <service-container>`
- Verify endpoint exists: `curl http://<service>:8000/internal/snapshot`
- Check network connectivity between services

### "Event consumption pause not implemented"

**Cause**: RabbitMQ service doesn't support pause (older version)

**Solution**:
- Ensure `PausableRabbitMQService` is being used
- Update `events.py` with pause/resume methods
- Restart read-model-updater service

### "Invalid or missing internal token"

**Cause**: X-INTERNAL-TOKEN header is missing or incorrect

**Solution**:
- Include header in request: `-H "X-INTERNAL-TOKEN: your-token"`
- Check token matches `INTERNAL_API_TOKEN` environment variable
- Verify token is set in docker-compose.yml

### "Rebuild timeout"

**Cause**: Snapshot fetching or rebuild taking too long

**Solution**:
- Increase `SNAPSHOT_REQUEST_TIMEOUT` environment variable
- Check domain service performance
- Consider pagination for large datasets
- Optimize database indexes

## Future Enhancements

1. **Incremental Rebuild**: Rebuild only specific projections
2. **Parallel Snapshot Fetching**: Use `asyncio.gather()` for faster fetching
3. **Resume from Failure**: Save checkpoint and resume if rebuild fails
4. **Scheduled Rebuilds**: Automatic periodic rebuilds
5. **Webhook Notifications**: Notify on rebuild completion
6. **Versioning**: Track rebuild version for rollback capability

## References

- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [Materialized View Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/materialized-view)
- [Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)
