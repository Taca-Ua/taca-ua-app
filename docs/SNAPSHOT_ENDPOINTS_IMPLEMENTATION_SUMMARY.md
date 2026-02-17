# Snapshot Endpoints Implementation Summary

## Overview

All domain microservices now have `/internal/snapshot` endpoints implemented for the Read Model Updater rebuild feature.

## Implemented Services

### ✅ Matches Service
**Endpoint**: `GET /internal/snapshot`

**Returns**:
- `matches`: All match records
- `participants`: All match participants
- `lineups`: All match lineups
- `comments`: All match comments

**File**: [matches-service/app/internal_controller.py](../src/microservices/matches-service/app/internal_controller.py)

---

### ✅ Tournaments Service
**Endpoint**: `GET /internal/snapshot`

**Returns**:
- `tournaments`: All tournament records
- `competitors`: All tournament competitors
- `ranking_positions`: All tournament ranking positions

**File**: [tournaments-service/app/internal_controller.py](../src/microservices/tournaments-service/app/internal_controller.py)

---

### ✅ Modalities Service
**Endpoint**: `GET /internal/snapshot`

**Returns**:
- `nucleos`: All nucleos
- `courses`: All courses
- `modality_types`: All modality types
- `modalities`: All modalities
- `students`: All students
- `staff`: All staff members
- `teams`: All teams
- `team_players`: All team-player relationships

**File**: [modalities-service/app/internal_controller.py](../src/microservices/modalities-service/app/internal_controller.py)

---

### ✅ Ranking Service
**Endpoint**: `GET /internal/snapshot`

**Returns**:
- `modality_rankings`: All modality rankings
- `course_rankings`: All course rankings
- `general_rankings`: All general rankings

**File**: [ranking-service/app/internal_controller.py](../src/microservices/ranking-service/app/internal_controller.py)

---

## Quick Testing

### Test Individual Endpoint (curl)

```bash
# Matches Service
curl http://localhost:8001/internal/snapshot | jq

# Tournaments Service
curl http://localhost:8002/internal/snapshot | jq

# Modalities Service
curl http://localhost:8003/internal/snapshot | jq

# Ranking Service
curl http://localhost:8004/internal/snapshot | jq
```

### Test from Docker Network

```bash
# From within a container
curl http://matches-service:8000/internal/snapshot
curl http://tournaments-service:8000/internal/snapshot
curl http://modalities-service:8000/internal/snapshot
curl http://ranking-service:8000/internal/snapshot
```

### Test All Endpoints

Use the provided test script:

```bash
python tools/test_snapshot_endpoints.py
```

---

## Testing the Full Rebuild Flow

### 1. Start All Services

```bash
docker-compose up -d
```

### 2. Verify Services Are Running

```bash
docker ps
```

### 3. Test Individual Snapshots

```bash
# Test matches snapshot
curl http://localhost:8001/internal/snapshot

# Test tournaments snapshot
curl http://localhost:8002/internal/snapshot

# Test modalities snapshot
curl http://localhost:8003/internal/snapshot

# Test ranking snapshot
curl http://localhost:8004/internal/snapshot
```

### 4. Trigger Rebuild

```bash
curl -X POST http://localhost:8000/internal/rebuild \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

### 5. Check Rebuild Status

```bash
curl http://localhost:8000/internal/rebuild/status \
  -H "X-INTERNAL-TOKEN: your-token-here"
```

---

## Response Format Examples

### Matches Service Response

```json
{
  "matches": [
    {
      "id": "uuid",
      "tournament_id": "uuid",
      "location": "Field A",
      "start_time": "2026-02-17T10:00:00+00:00",
      "status": "scheduled",
      "created_by": "uuid",
      "created_at": "2026-02-17T08:00:00+00:00",
      "updated_at": null
    }
  ],
  "participants": [...],
  "lineups": [...],
  "comments": [...]
}
```

### Modalities Service Response

```json
{
  "nucleos": [...],
  "courses": [...],
  "modality_types": [...],
  "modalities": [...],
  "students": [...],
  "staff": [...],
  "teams": [...],
  "team_players": [
    {
      "team_id": "uuid",
      "student_id": "uuid"
    }
  ]
}
```

---

## Data Flow

```
1. Read Model Updater triggers rebuild
   ↓
2. Pauses event consumption
   ↓
3. Clears projection tables
   ↓
4. Fetches snapshots from all services:
   - GET matches-service:8000/internal/snapshot
   - GET tournaments-service:8000/internal/snapshot
   - GET modalities-service:8000/internal/snapshot
   - GET ranking-service:8000/internal/snapshot
   ↓
5. Rebuilds projections from snapshot data
   ↓
6. Resumes event consumption
```

---

## Security Notes

### Current Implementation

- ✅ Endpoints are on `/internal` path
- ✅ Structured logging for all requests
- ⚠️  No authentication (relying on network isolation)

### Recommended Production Setup

Add authentication to snapshot endpoints:

```python
from fastapi import Header, HTTPException
import os

@router.get("/snapshot")
def get_snapshot(
    db: Session = Depends(get_db_session),
    x_internal_token: str = Header(...),
):
    # Verify token
    if x_internal_token != os.getenv("INTERNAL_API_TOKEN"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ... rest of implementation
```

Then add to docker-compose.yml:

```yaml
environment:
  - INTERNAL_API_TOKEN=your-secure-token
```

---

## Troubleshooting

### Issue: "Connection refused"

**Solution**: Verify service is running and port is correct
```bash
docker ps
docker logs <service-container>
```

### Issue: "Empty response"

**Solution**: Check if database has data
```bash
docker exec -it postgres psql -U user -d taca_db
SELECT COUNT(*) FROM matches.match;
```

### Issue: "Timeout"

**Solution**: Increase timeout or optimize queries
```python
# In Read Model Updater config.py
SNAPSHOT_REQUEST_TIMEOUT=60  # Increase from 30
```

### Issue: "JSON serialization error"

**Solution**: Check that all datetime fields use `.isoformat()` and enums use `.value`

---

## File Changes Summary

### New Files Created (4)

1. `src/microservices/matches-service/app/internal_controller.py`
2. `src/microservices/tournaments-service/app/internal_controller.py`
3. `src/microservices/modalities-service/app/internal_controller.py`
4. `src/microservices/ranking-service/app/internal_controller.py`

### Modified Files (4)

1. `src/microservices/matches-service/app/main.py` - Registered internal router
2. `src/microservices/tournaments-service/app/main.py` - Registered internal router
3. `src/microservices/modalities-service/app/main.py` - Registered internal router
4. `src/microservices/ranking-service/app/main.py` - Registered internal router

### Utility Files (1)

1. `tools/test_snapshot_endpoints.py` - Testing script

---

## Next Steps

### 1. Test Locally

```bash
# Start services
docker-compose up -d

# Test snapshots
python tools/test_snapshot_endpoints.py
```

### 2. Trigger Test Rebuild

```bash
curl -X POST http://localhost:8000/internal/rebuild \
  -H "X-INTERNAL-TOKEN: change-me-in-production"
```

### 3. Verify Results

```bash
# Check rebuild status
curl http://localhost:8000/internal/rebuild/status \
  -H "X-INTERNAL-TOKEN: change-me-in-production"

# Check database
docker exec -it postgres psql -U user -d taca_db
SELECT COUNT(*) FROM public_read.matches;
```

### 4. Add Security (Production)

- Set unique `INTERNAL_API_TOKEN` in production
- Add token verification to snapshot endpoints
- Consider network isolation (internal Docker network)

### 5. Monitor Performance

- Check snapshot fetch duration
- Monitor database load during rebuild
- Adjust timeouts if needed

---

## Related Documentation

- [READ_MODEL_REBUILD_FEATURE.md](./READ_MODEL_REBUILD_FEATURE.md) - Full rebuild documentation
- [SNAPSHOT_ENDPOINT_IMPLEMENTATION_GUIDE.md](./SNAPSHOT_ENDPOINT_IMPLEMENTATION_GUIDE.md) - Implementation guide

---

## Summary

✅ **All 4 microservices now have snapshot endpoints**
✅ **Endpoints return complete domain data**
✅ **Structured logging implemented**
✅ **Test script provided**
✅ **Ready for Read Model Updater integration**

The rebuild feature is now fully implemented and ready to use! 🎉
