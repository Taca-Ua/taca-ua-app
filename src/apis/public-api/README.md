# Public API

Public read-only API for TACA competition data. This API exposes materialized views from the `public_read` schema that aggregate data from multiple microservices.

## Overview

- **No Authentication Required**: This API is publicly accessible
- **Read-Only**: All endpoints are GET requests only
- **Data Source**: Materialized views maintained by the read-model-updater service
- **Base URL**: `/api/public`
- **Documentation**: `/api/public/docs` (Swagger UI)

## Architecture

The Public API follows a clean separation of concerns:

```
┌─────────────────┐
│  Microservices  │  (Modalities, Tournaments, Matches, etc.)
└────────┬────────┘
         │ Events
         v
┌─────────────────┐
│ Read Model      │  Updates materialized views
│ Updater         │
└────────┬────────┘
         │ Writes
         v
┌─────────────────┐
│ Materialized    │  (public_read schema)
│ Views           │
└────────┬────────┘
         │ Reads
         v
┌─────────────────┐
│ Public API      │  Exposes views via REST
└─────────────────┘
```

## Available Endpoints

### Health & Status

#### `GET /`
Root endpoint with service information.

**Response:**
```json
{
  "status": "healthy",
  "service": "Public API",
  "timestamp": "2026-02-27T10:00:00Z"
}
```

#### `GET /health`
Health check with database connection verification.

---

### Teams

#### `GET /teams`
List all teams with pagination and optional filters.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 50, max: 100): Items per page
- `course_id` (UUID, optional): Filter by course
- `nucleo_id` (UUID, optional): Filter by nucleo
- `modality_id` (UUID, optional): Filter by modality

**Response:**
```json
{
  "items": [
    {
      "team_id": "uuid",
      "team_name": "string",
      "course_id": "uuid",
      "course_name": "string",
      "course_abbreviation": "string",
      "nucleo_id": "uuid",
      "nucleo_name": "string",
      "nucleo_abbreviation": "string",
      "modality_id": "uuid",
      "modality_name": "string",
      "modality_type_id": "uuid",
      "modality_type_name": "string",
      "player_count": 0,
      "updated_at": "2026-02-27T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

#### `GET /teams/{team_id}`
Get detailed information about a specific team.

**Parameters:**
- `team_id` (UUID): Unique identifier of the team

**Response:** Single team object (same structure as items in list)

---

### Students

#### `GET /students`
List all students with pagination and optional filters.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 50, max: 100): Items per page
- `course_id` (UUID, optional): Filter by course
- `nucleo_id` (UUID, optional): Filter by nucleo
- `is_member` (bool, optional): Filter by membership status
- `search` (string, optional): Search in student name or number

**Response:**
```json
{
  "items": [
    {
      "student_id": "uuid",
      "student_number": "string",
      "full_name": "string",
      "is_member": true,
      "course_id": "uuid",
      "course_name": "string",
      "course_abbreviation": "string",
      "nucleo_id": "uuid",
      "nucleo_name": "string",
      "nucleo_abbreviation": "string",
      "team_count": 0,
      "updated_at": "2026-02-27T10:00:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "page_size": 50
}
```

#### `GET /students/{student_id}`
Get detailed information about a specific student.

#### `GET /students/by-number/{student_number}`
Get student information by their student number.

---

### Tournaments

#### `GET /tournaments`
List all tournaments with pagination and optional filters.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 50, max: 100): Items per page
- `modality_id` (UUID, optional): Filter by modality
- `status` (string, optional): Filter by status (draft, active, finished, cancelled)

**Response:**
```json
{
  "items": [
    {
      "tournament_id": "uuid",
      "tournament_name": "string",
      "start_date": "2026-02-27",
      "status": "active",
      "modality_id": "uuid",
      "modality_name": "string",
      "modality_type_id": "uuid",
      "modality_type_name": "string",
      "competitor_count": 8,
      "match_count": 15,
      "updated_at": "2026-02-27T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 50
}
```

#### `GET /tournaments/{tournament_id}`
Get detailed information about a specific tournament.

#### `GET /tournaments/{tournament_id}/standings`
Get the current standings/rankings for a tournament.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 50, max: 100): Items per page

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "tournament_id": "uuid",
      "competitor_type": "team",
      "competitor_entity_id": "uuid",
      "competitor_name": "string",
      "matches_played": 5,
      "wins": 3,
      "losses": 1,
      "draws": 1,
      "points": 10,
      "total_score": 45,
      "rank": 1,
      "statistics_metadata": {},
      "updated_at": "2026-02-27T10:00:00Z"
    }
  ],
  "total": 8,
  "page": 1,
  "page_size": 50
}
```

---

### Matches

#### `GET /matches`
List all matches with pagination and optional filters.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 50, max: 100): Items per page
- `tournament_id` (UUID, optional): Filter by tournament
- `status` (string, optional): Filter by status (scheduled, in_progress, completed, finished, cancelled)

**Response:**
```json
{
  "items": [
    {
      "match_id": "uuid",
      "location": "Pavilhão de Desportos",
      "status": "completed",
      "start_time": "2026-02-27T15:00:00Z",
      "tournament_id": "uuid",
      "tournament_name": "string",
      "modality_id": "uuid",
      "modality_name": "string",
      "participants": [
        {
          "participant_id": "uuid",
          "participant_type": "team",
          "participant_entity_id": "uuid",
          "name": "Team A"
        }
      ],
      "results": [
        {
          "participant_id": "uuid",
          "score": 25,
          "position": 1
        }
      ],
      "participant_count": 2,
      "comment_count": 5,
      "updated_at": "2026-02-27T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

#### `GET /matches/{match_id}`
Get detailed information about a specific match, including participants, results, and statistics.

---

### Competitor Standings

#### `GET /competitors/{competitor_id}/standings`
Get all tournament standings for a specific competitor (team or athlete).

**Parameters:**
- `competitor_id` (UUID): Team ID or Student ID

**Response:** Array of tournament standings for this competitor across all tournaments they've participated in.

---

## Pagination

All list endpoints support pagination with the following parameters:

- `page`: Page number (starts at 1)
- `page_size`: Number of items per page (max 100)

All paginated responses include:
```json
{
  "items": [...],
  "total": 0,
  "page": 1,
  "page_size": 50
}
```

## Error Responses

All endpoints may return the following error responses:

- `404 Not Found`: Resource not found
- `503 Service Unavailable`: Database connection issues

Error response format:
```json
{
  "detail": "Error message"
}
```

## Development

### Running Locally

The service requires the following environment variables:

```bash
DATABASE_URL=postgresql://tacauser:tacapassword@postgres:5432/tacadb
```

### Docker

Build and run with Docker:

```bash
# Development
docker-compose -f docker-compose.dev.yml up public-api

# Production
docker-compose up public-api
```

### Testing

The API documentation is available at `/api/public/docs` when running, where you can test all endpoints interactively.

## Data Model

All data is sourced from the following materialized views in the `public_read` schema:

- `mv_team_details`: Team information with course, nucleo, and modality details
- `mv_student_details`: Student information with course and nucleo details
- `mv_tournament_details`: Tournament information with modality details
- `mv_match_details`: Match information with participants and results
- `mv_tournament_standings`: Tournament standings/rankings

These views are automatically maintained by the read-model-updater service.

## Monitoring

- **Prometheus Metrics**: Available at `/metrics`
- **Health Check**: Available at `/health`
- **Structured Logging**: All requests are logged with structured JSON format

## Schema Validation

All API responses are validated using Pydantic schemas to ensure data consistency and type safety.
