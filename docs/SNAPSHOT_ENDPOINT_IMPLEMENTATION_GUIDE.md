# Snapshot Endpoint Implementation Guide

## Quick Reference for Domain Service Developers

This guide shows how to implement the `/internal/snapshot` endpoint in your domain microservice.

## Overview

The Read Model Updater needs to fetch complete snapshots of your domain data to rebuild projections. Your service must expose an internal endpoint that returns all relevant data.

## Basic Implementation

### 1. Create Internal Router (FastAPI)

```python
# app/internal_controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db

router = APIRouter(prefix="/internal", tags=["internal"])

@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db)):
    """
    Return complete snapshot of all domain data.

    This endpoint should be internal-only and NOT exposed via API Gateway.
    Returns all data needed for read model projections.
    """
    # Import your models
    from .models import Match, MatchParticipant, MatchResult, ...

    # Fetch all data
    matches = db.query(Match).all()
    participants = db.query(MatchParticipant).all()
    results = db.query(MatchResult).all()
    # ... more queries

    # Convert to dictionaries
    return {
        "matches": [match_to_dict(m) for m in matches],
        "participants": [participant_to_dict(p) for p in participants],
        "results": [result_to_dict(r) for r in results],
        # ... more data
    }
```

### 2. Helper Function to Convert Models to Dicts

```python
def match_to_dict(match):
    """Convert Match model to dictionary."""
    return {
        "id": match.id,
        "tournament_id": match.tournament_id,
        "match_date": match.match_date.isoformat() if match.match_date else None,
        "status": match.status.value if match.status else None,
        "created_at": match.created_at.isoformat() if match.created_at else None,
        # ... all fields needed for read model
    }
```

**Tip**: If using Pydantic models, you can use `.model_dump()` or `.dict()`:
```python
return {
    "matches": [MatchSchema.model_validate(m).model_dump() for m in matches],
}
```

### 3. Register Router in Main App

```python
# app/main.py
from .internal_controller import router as internal_router

app = FastAPI(...)

# Include internal router
app.include_router(internal_router)
```

## What Data to Include

### Required Fields

Include ALL fields that appear in read model projections:
- Primary keys (ids)
- Foreign keys (relationships)
- Business data (names, dates, statuses)
- Timestamps (created_at, updated_at)

### Optional Fields

You can omit:
- Sensitive data not in read models (passwords, tokens)
- Large binary data (files, images) - unless needed
- Computed fields that can be derived

## Example: Matches Service

```python
# app/internal_controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Match, MatchParticipant, MatchResult, MatchLineup, MatchComment

router = APIRouter(prefix="/internal", tags=["internal"])

@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db)):
    """Return complete matches snapshot."""

    # Fetch all matches data
    matches = db.query(Match).all()
    participants = db.query(MatchParticipant).all()
    results = db.query(MatchResult).all()
    lineups = db.query(MatchLineup).all()
    comments = db.query(MatchComment).all()

    return {
        "matches": [
            {
                "id": m.id,
                "tournament_id": m.tournament_id,
                "match_date": m.match_date.isoformat() if m.match_date else None,
                "location": m.location,
                "status": m.status.value,
                "created_at": m.created_at.isoformat(),
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            }
            for m in matches
        ],
        "participants": [
            {
                "id": p.id,
                "match_id": p.match_id,
                "team_id": p.team_id,
                "participant_type": p.participant_type.value,
            }
            for p in participants
        ],
        "results": [
            {
                "id": r.id,
                "match_id": r.match_id,
                "team_id": r.team_id,
                "score": r.score,
                "position": r.position,
            }
            for r in results
        ],
        "lineups": [
            {
                "id": l.id,
                "match_id": l.match_id,
                "team_id": l.team_id,
                "student_id": l.student_id,
                "position": l.position,
            }
            for l in lineups
        ],
        "comments": [
            {
                "id": c.id,
                "match_id": c.match_id,
                "author": c.author,
                "content": c.content,
                "created_at": c.created_at.isoformat(),
            }
            for c in comments
        ],
    }
```

## Example: Tournament Service

```python
@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db)):
    """Return complete tournament snapshot."""

    tournaments = db.query(Tournament).all()
    competitors = db.query(TournamentCompetitor).all()

    return {
        "tournaments": [
            {
                "id": t.id,
                "name": t.name,
                "modality_id": t.modality_id,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
            }
            for t in tournaments
        ],
        "competitors": [
            {
                "id": c.id,
                "tournament_id": c.tournament_id,
                "team_id": c.team_id,
                "seed": c.seed,
                "joined_at": c.joined_at.isoformat(),
            }
            for c in competitors
        ],
    }
```

## Example: Modalities Service

```python
@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db)):
    """Return complete modalities snapshot."""

    return {
        "nucleos": [n.to_dict() for n in db.query(Nucleo).all()],
        "courses": [c.to_dict() for c in db.query(Course).all()],
        "modality_types": [mt.to_dict() for mt in db.query(ModalityType).all()],
        "modalities": [m.to_dict() for m in db.query(Modality).all()],
        "students": [s.to_dict() for s in db.query(Student).all()],
        "staff": [s.to_dict() for s in db.query(Staff).all()],
        "teams": [t.to_dict() for t in db.query(Team).all()],
        "team_players": [tp.to_dict() for tp in db.query(TeamPlayer).all()],
    }
```

## Handling Large Datasets

If your service has a lot of data (>10,000 records), consider:

### Option 1: Pagination

```python
@router.get("/snapshot")
def get_snapshot(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 1000,
):
    offset = (page - 1) * page_size

    matches = db.query(Match).offset(offset).limit(page_size).all()

    return {
        "matches": [m.to_dict() for m in matches],
        "page": page,
        "page_size": page_size,
        "total": db.query(Match).count(),
        "has_more": offset + page_size < db.query(Match).count(),
    }
```

### Option 2: Streaming

```python
from fastapi.responses import StreamingResponse
import json

@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db)):
    def generate():
        yield '{"matches": ['
        first = True
        for match in db.query(Match).yield_per(100):
            if not first:
                yield ','
            yield json.dumps(match.to_dict())
            first = False
        yield ']}'

    return StreamingResponse(generate(), media_type="application/json")
```

### Option 3: Compressed Response

```python
import gzip
import json

@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db)):
    data = {
        "matches": [m.to_dict() for m in db.query(Match).all()],
        # ... more data
    }

    compressed = gzip.compress(json.dumps(data).encode())

    return Response(
        content=compressed,
        media_type="application/json",
        headers={"Content-Encoding": "gzip"},
    )
```

## Handling Enum Types

If you use SQLAlchemy enums:

```python
from enum import Enum

# Your enum
class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# In snapshot endpoint
{
    "status": match.status.value if match.status else None,
    # NOT: "status": match.status  (this won't serialize)
}
```

## Handling Dates and Times

Always convert datetime objects to ISO strings:

```python
{
    "created_at": match.created_at.isoformat() if match.created_at else None,
    "match_date": match.match_date.isoformat() if match.match_date else None,
}
```

## Testing Your Endpoint

### Test Locally

```bash
# Start your service
uvicorn app.main:app --reload --port 8000

# Test snapshot endpoint
curl http://localhost:8000/internal/snapshot
```

### Test Response Structure

```python
import requests

response = requests.get("http://localhost:8000/internal/snapshot")
data = response.json()

# Verify structure
assert "matches" in data
assert isinstance(data["matches"], list)
assert len(data["matches"]) > 0
assert "id" in data["matches"][0]
```

### Test from Read Model Updater

```bash
# From within Docker network
docker exec -it read-model-updater curl http://matches-service:8000/internal/snapshot
```

## Security Considerations

### Option 1: Internal Token (Recommended)

```python
from fastapi import Header, HTTPException

@router.get("/snapshot")
def get_snapshot(
    db: Session = Depends(get_db),
    x_internal_token: str = Header(...),
):
    if x_internal_token != os.getenv("INTERNAL_API_TOKEN"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ... return snapshot
```

### Option 2: Network Isolation

Configure Docker networks to ensure snapshot endpoints are only accessible internally:

```yaml
# docker-compose.yml
services:
  matches-service:
    networks:
      - internal
      - public

  read-model-updater:
    networks:
      - internal

networks:
  internal:
    driver: bridge
  public:
    driver: bridge
```

### Option 3: IP Whitelist

```python
from fastapi import Request

@router.get("/snapshot")
def get_snapshot(request: Request, db: Session = Depends(get_db)):
    # Only allow internal Docker IPs
    client_ip = request.client.host
    if not client_ip.startswith("172."):  # Docker internal network
        raise HTTPException(status_code=403, detail="Forbidden")

    # ... return snapshot
```

## Troubleshooting

### "TypeError: Object of type datetime is not JSON serializable"

**Fix**: Convert datetime to ISO string
```python
created_at: match.created_at.isoformat() if match.created_at else None
```

### "TypeError: Object of type Enum is not JSON serializable"

**Fix**: Use `.value` to get enum string value
```python
status: match.status.value if match.status else None
```

### "Connection timeout"

**Fix**: Increase timeout in Read Model Updater config:
```env
SNAPSHOT_REQUEST_TIMEOUT=60
```

### "Response too large"

**Fix**: Implement pagination or compression (see "Handling Large Datasets")

## Checklist

Before deploying your snapshot endpoint:

- [ ] Endpoint returns all data needed for read models
- [ ] All datetime fields are converted to ISO strings
- [ ] All enum fields use `.value` to get string representation
- [ ] Response can be serialized to JSON
- [ ] Tested locally with curl
- [ ] Tested from Read Model Updater (if possible)
- [ ] Security measures in place (token, network isolation, etc.)
- [ ] Large datasets handled appropriately (pagination/compression)
- [ ] Logging added for monitoring
- [ ] Error handling for database failures

## Next Steps

After implementing your snapshot endpoint:

1. **Update Read Model Updater**: Ensure your service URL is in `docker-compose.yml`
2. **Test Rebuild**: Trigger a rebuild and verify your data appears correctly
3. **Monitor Performance**: Check snapshot fetch duration and optimize if needed
4. **Document**: Add notes about any special fields or considerations

## Questions?

See the main rebuild documentation: [READ_MODEL_REBUILD_FEATURE.md](./READ_MODEL_REBUILD_FEATURE.md)
