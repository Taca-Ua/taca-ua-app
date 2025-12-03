# Frontend API Structure

The API is now organized in the `/src/api/` directory with clean separation:

## Structure

```
src/api/
├── index.ts          # Main export file
├── client.ts         # Core API client and utilities
├── types.ts          # All TypeScript types
├── courses.ts        # Courses API
├── seasons.ts        # Seasons API
├── modalities.ts     # Modalities API
├── teams.ts          # Teams API
├── matches.ts        # Matches/Calendar API
├── tournaments.ts    # Tournaments API
├── rankings.ts       # Rankings API
├── regulations.ts    # Regulations API
└── history.ts        # Historical data API
```

## Usage Examples

### Simple import (recommended):
```typescript
import { api } from '@/api';

// Use it
const matches = await api.matches.getMatches({ date: '2025-12-03' });
const courses = await api.courses.getCourses();
const rankings = await api.rankings.getGeneralRanking();
```

### Import specific modules:
```typescript
import { matchesApi, coursesApi } from '@/api';

const matches = await matchesApi.getMatches();
const courses = await coursesApi.getCourses();
```

### Import types:
```typescript
import type { Match, Course, Modality } from '@/api';
```

## Configuration

Set the API base URL in `.env.development`:
```
VITE_API_BASE_URL=http://localhost/api/public
```

## Benefits

✅ Clean imports - no clutter in components
✅ Organized by domain/resource
✅ Type-safe with TypeScript
✅ Reusable across all pages
✅ Easy to maintain and extend
