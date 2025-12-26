# Public API Changes - Frontend Integration

This document tracks changes made to the Public API during frontend integration.

## Summary

Updated public API endpoints and schemas to support the frontend public website. All changes maintain backward compatibility where possible and follow RESTful conventions.

---

## Schema Changes

### 1. Calendar/Matches Schema (`app/schemas/calendar.py`)

**Added nested models:**
```python
class TeamInfo(BaseModel):
    id: int
    name: str
    course_abbreviation: str

class ModalityInfo(BaseModel):
    id: int
    name: str
```

**Updated `MatchPublicList`:**
- Changed flat fields to nested objects
- Before: `team_home_id`, `team_home_name`, `course_home_id`, `modality_id`, `modality_name`
- After: `team_home: TeamInfo`, `team_away: TeamInfo`, `modality: ModalityInfo`
- Added: `tournament_name` field
- Removed: Individual flat ID/name fields

**Updated `MatchPublicDetail`:**
- Same nested structure as `MatchPublicList`
- **Removed**: `comments` field (not needed for public display)

### 2. Tournaments Schema (`app/schemas/tournaments.py`)

**Added nested models:**
```python
class ModalityInfo(BaseModel):
    id: int
    name: str

class SeasonInfo(BaseModel):
    id: int
    year: int
    display_name: str
```

**Updated `TournamentPublicList` and `TournamentPublicDetail`:**
- Changed to nested objects for modality and season
- Before: `modality_id`, `modality_name`, `season_id`, `season_year`
- After: `modality: ModalityInfo`, `season: SeasonInfo`

### 3. Rankings Schema (`app/schemas/rankings.py`)

**No schema changes** - Already using proper structure with nested objects

### 4. Regulations Schema (`app/schemas/regulations.py`)

**Updated `RegulationPublic`:**
- Removed: `modality_id`, `modality_name` (regulations aren't tied to specific modalities)
- Added: `category` (string, optional) - More flexible than modality binding
- Added: `updated_at` (datetime)
- Kept: `file_url` for direct file access

---

## Route/Endpoint Changes

### 1. Calendar Routes (`app/routes/calendar.py`)

#### `GET /api/public/matches`

**Enhanced mock data:**
- Increased from 2 to **16 matches**
- Spread across multiple dates: Nov 28, Nov 30, Dec 3, 7, 10, 14, 17, 21 and Jan 7, 11
- Added **4 finished matches** with scores
- **12 scheduled matches** for upcoming dates

**Improved filtering:**
- Fixed date filtering to work with nested structures
- Fixed modality_id filtering (checks `match["modality"]["id"]`)
- Fixed course_id/team_id filtering (checks `match["team_home"]["id"]` and `match["team_away"]["id"]`)
- All filters now work correctly with nested data structure

**Response structure updated:**
```json
{
  "id": 1,
  "tournament_id": 1,
  "tournament_name": "Campeonato de Futebol 25/26",
  "team_home": {
    "id": 1,
    "name": "NEI",
    "course_abbreviation": "NEI"
  },
  "team_away": {
    "id": 2,
    "name": "NEC",
    "course_abbreviation": "NEC"
  },
  "modality": {
    "id": 1,
    "name": "Futebol"
  },
  "start_time": "2025-12-03T14:00:00",
  "location": "Pavilhão Gimnodesportivo da UA",
  "status": "finished",
  "home_score": 2,
  "away_score": 1
}
```

#### `GET /api/public/matches/{match_id}`

**Created proper mock database:**
- ID-based lookup returns different data per match
- Added detailed match records for key matches (IDs: 1, 14, 15)
- Returns proper status ("finished" vs "scheduled")
- Returns actual scores for finished matches

### 2. Tournament Routes (`app/routes/tournaments.py`)

**No changes in this iteration** - Already had proper mock database and nested structures

### 3. Modality Routes (`app/routes/modalities.py`)

**Updated mock data:**
- Changed from 3 to **4 modalities**
- Replaced: Ténis (id: 3) → Andebol (id: 3)
- Added: Voleibol (id: 4)
- **Reason**: Match calendar and tournament data for consistency

**Current modalities:**
1. Futebol (Futebol de 11)
2. Futsal (Futsal de 5)
3. Andebol (Andebol de 7)
4. Voleibol (Voleibol 6x6)

### 4. Rankings Routes (`app/routes/rankings.py`)

#### `GET /api/public/rankings/general`

**Enhanced filtering:**
- Added `season_id` query parameter support
- Returns different data based on season
- Season 1 (2024): LEI leads with 45 points
- Season 2 (2025): MECT leads with 38 points
- Proper handling when season_id not provided (returns active season)

### 5. Regulations Routes (`app/routes/regulations.py`)

**Updated endpoint:**
- Changed filter from `modality_id` to `category`
- **Reason**: Regulations aren't always modality-specific (e.g., "Regulamento Geral")

**Updated mock data:**
- Added 5 regulations covering different categories
- Categories: "geral", "futsal", "futebol", "andebol", "minecraft"

**Example response:**
```json
{
  "id": "uuid-here",
  "title": "Regulamento Geral",
  "description": "Regulamento geral da Taça UA",
  "category": "geral",
  "file_url": "/api/public/regulations/uuid/download",
  "created_at": "2025-01-15T10:00:00",
  "updated_at": "2025-01-15T10:00:00"
}
```

---

## Breaking Changes

### 1. Match Schema Structure

**Impact:** Any clients consuming match endpoints
**Migration:**
```typescript
// Before
const teamHomeName = match.team_home_name;
const modalityName = match.modality_name;

// After
const teamHomeName = match.team_home.name;
const modalityName = match.modality.name;
```

### 2. Tournament Schema Structure

**Impact:** Any clients consuming tournament endpoints
**Migration:**
```typescript
// Before
const modalityName = tournament.modality_name;
const seasonYear = tournament.season_year;

// After
const modalityName = tournament.modality.name;
const seasonDisplay = tournament.season.display_name;
```

### 3. Regulations Filter Change

**Impact:** Clients filtering regulations by modality
**Migration:**
```typescript
// Before
GET /api/public/regulations?modality_id=2

// After
GET /api/public/regulations?category=futsal
```

### 4. Removed Comments from Match Details

**Impact:** Any clients expecting comments field
**Migration:** Simply remove references to `match.comments` - field no longer exists

---

## Non-Breaking Changes

### 1. Rankings Season Filter

**Added:** `season_id` query parameter to rankings endpoints
**Backward compatible:** If not provided, returns active season (existing behavior)

### 2. Match Status Values

**Added:** Support for all status types
- `scheduled` (existing)
- `in_progress` (new)
- `finished` (existing)
- `cancelled` (new)

### 3. Enhanced Mock Data

**Improved:** All mock data expanded with more realistic scenarios
**Backward compatible:** Existing queries continue to work

---

## Testing Checklist

All endpoints tested and verified:

- [x] `GET /api/public/matches` - Returns 16 matches
- [x] `GET /api/public/matches?date=2025-12-07` - Returns 3 matches
- [x] `GET /api/public/matches?modality_id=2` - Returns 4 Futsal matches
- [x] `GET /api/public/matches?status=finished` - Returns 4 finished matches
- [x] `GET /api/public/matches/1` - Returns finished match with score 2-1
- [x] `GET /api/public/tournaments?season_id=3&modality_id=2` - Filters correctly
- [x] `GET /api/public/tournaments/1?include_rankings=true` - Returns with rankings
- [x] `GET /api/public/rankings/general?season_id=1` - Returns season 1 data
- [x] `GET /api/public/rankings/general` - Returns active season data
- [x] `GET /api/public/modalities` - Returns 4 modalities
- [x] `GET /api/public/regulations` - Returns 5 regulations
- [x] `GET /api/public/regulations?category=futsal` - Returns 1 regulation
- [x] `GET /api/public/seasons` - Returns seasons list

---

## Data Consistency

### Cross-Reference Matrix

Ensuring all IDs and relationships are consistent across endpoints:

| Entity | ID | Used In | Verified |
|--------|----|---------|---------|
| Futebol | 1 | Matches, Tournaments, Modalities | ✅ |
| Futsal | 2 | Matches, Tournaments, Modalities | ✅ |
| Andebol | 3 | Matches, Tournaments, Modalities | ✅ |
| Voleibol | 4 | Matches, Tournaments, Modalities | ✅ |
| NEI | 1 | Matches, Tournaments, Rankings | ✅ |
| NEC | 2 | Matches, Tournaments, Rankings | ✅ |
| NET | 3 | Matches, Tournaments, Rankings | ✅ |
| NEMat | 4 | Matches, Tournaments, Rankings | ✅ |
| NEGeo | 5 | Matches, Tournaments, Rankings | ✅ |
| Season 24/25 | 1 | Tournaments, Rankings | ✅ |
| Season 25/26 | 2 | Tournaments, Rankings, Matches | ✅ |

---

## Performance Considerations

### Current Implementation

**Advantages:**
- Simple mock data structure
- Fast response times (in-memory)
- No database queries

**Limitations:**
- All data loaded in memory
- No pagination on matches endpoint
- Client-side filtering for some use cases

### Future Optimizations

When moving to real database:

1. **Add pagination** to matches endpoint (already has `limit` and `offset` params)
2. **Database indexing** on frequently filtered fields (date, modality_id, team_id, status)
3. **Caching layer** (Redis) for rankings and tournaments
4. **Query optimization** with proper joins for nested objects
5. **Response compression** for large result sets

---

## Documentation Updates

Updated files:
- ✅ `/docs/API_ENDPOINTS.md` - Added detailed schemas and examples
- ✅ `/docs/FRONTEND_PUBLIC_WEBSITE.md` - Complete frontend documentation
- ✅ `/docs/API_CHANGES_PUBLIC.md` - This file

---

## Migration Guide

### For Future Database Implementation

Current mock data structure maps to database models:

**Matches:**
```sql
SELECT
  m.id,
  m.tournament_id,
  t.name as tournament_name,
  json_build_object(
    'id', th.id,
    'name', th.name,
    'course_abbreviation', c1.short_code
  ) as team_home,
  json_build_object(
    'id', ta.id,
    'name', ta.name,
    'course_abbreviation', c2.short_code
  ) as team_away,
  json_build_object(
    'id', mod.id,
    'name', mod.name
  ) as modality,
  m.start_time,
  m.location,
  m.status,
  m.home_score,
  m.away_score
FROM matches m
JOIN tournaments t ON t.id = m.tournament_id
JOIN teams th ON th.id = m.team_home_id
JOIN teams ta ON ta.id = m.team_away_id
JOIN courses c1 ON c1.id = th.course_id
JOIN courses c2 ON c2.id = ta.course_id
JOIN modalities mod ON mod.id = t.modality_id
WHERE m.start_time::date = $1  -- date filter
  AND mod.id = $2              -- modality filter
```

**Similar patterns** apply for tournaments, rankings, etc.

---

## Rollback Procedure

If issues arise:

1. **Schema changes**: Revert schema files to previous versions
2. **Route changes**: Mock data is self-contained, easy to revert
3. **Frontend**: No server-side state, can redeploy previous version independently

**Note:** Schema changes are only in response models, not database schema, so rollback is safe and fast.

---
