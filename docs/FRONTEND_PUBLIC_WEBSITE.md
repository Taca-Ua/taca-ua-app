# Frontend - Public Website

## Overview

The public website is a React application built with TypeScript, Vite, and Tailwind CSS. It provides a public-facing interface for viewing competition data without authentication.

**Technology Stack:**
- React 18
- TypeScript
- Vite 7.2.4
- Tailwind CSS
- React Router DOM

**Base Path:** `/src/frontend/public-website`

---

## Architecture

### API Client Structure

Located in `/src/frontend/public-website/src/api/`, the API client is organized by domain:

```
api/
├── client.ts          # Base API client with fetch wrapper
├── types.ts           # TypeScript interfaces for all API responses
├── index.ts           # Export all API modules
├── matches.ts         # Calendar/matches endpoints
├── rankings.ts        # Rankings endpoints
├── tournaments.ts     # Tournament endpoints
├── modalities.ts      # Modalities endpoints
├── seasons.ts         # Seasons endpoints
├── courses.ts         # Courses endpoints
├── teams.ts           # Teams endpoints
└── regulations.ts     # Regulations endpoints
```

#### Base Configuration

The API client uses environment variables:
- `VITE_API_BASE_URL` - Default: `http://localhost/api/public`

All API calls go through the centralized `apiCall` function which handles:
- Base URL prefixing
- Error handling
- JSON parsing
- Type safety with generics

---

## Pages

### 1. Home (`/`)

Landing page for the public website.

**File:** `src/pages/Home.tsx`

### 2. General Classification (`/classificacao/geral`)

Displays general rankings across all courses.

**File:** `src/pages/classificacao/Geral.tsx`

**Features:**
- Season filter (displays season `display_name`)
- Rankings table showing courses with J/V/E/D/Points
- Fetches from: `GET /api/public/rankings/general?season_id={id}`

**State Management:**
- Loads seasons on mount
- Sets active season as default
- Re-fetches rankings when season changes

### 3. Modality Classification (`/classificacao/modalidade`)

Shows tournaments grouped by modality and season.

**File:** `src/pages/classificacao/Modalidade.tsx`

**Features:**
- Season filter
- Modality filter with "All Modalities" option
- Tournament cards grid display
- Fetches from: `GET /api/public/tournaments?season_id={id}&modality_id={id}`

**Card Layout:**
- Tournament icon (🏆)
- Tournament name
- Modality name
- Season display name
- "Ver Classificação →" button (sticky to bottom)

### 4. Tournament Detail (`/classificacao/torneio/:id`)

Detailed view of a specific tournament with rankings.

**File:** `src/pages/classificacao/TorneioDetail.tsx`

**Features:**
- Tournament information (name, modality, season, rules)
- Rankings table with team statistics
- Fetches from: `GET /api/public/tournaments/{id}?include_rankings=true`

**Rankings Display:**
- Position
- Team name + Course (short code + full name)
- Match statistics: J (played), V (won), E (drawn), D (lost), Points

### 5. Calendar (`/calendario`)

Interactive calendar showing scheduled and finished matches.

**File:** `src/pages/Calendario.tsx`

**Features:**
- Month navigation (previous/next buttons)
- Calendar grid with day selection
- Modality filter (Futebol, Futsal, Andebol, Voleibol, All)
- Núcleo/Team filter (NEI, NEC, NET, NEMat, NEGeo, All)
- Current date auto-selected on load
- Visual indicators for days with matches (red text + dot)
- Match cards display for selected date
- Match detail modal

**API Calls:**
- `GET /api/public/modalities` - Load filter options
- `GET /api/public/matches` - Load all matches (client-side filtering)

**Match Card Display:**
- Tournament name
- Team names (home vs away)
- Modality name
- Time (HH:MM format)

**Match Detail Modal:**
- Tournament name
- Team abbreviations in colored circles
- Score display (if finished) or "VS" (if scheduled)
- Location, Time, Modality, Status
- Status translation:
  - `scheduled` → "Agendado"
  - `in_progress` → "Em Progresso"
  - `finished` → "Terminado"
  - `cancelled` → "Cancelado"

### 6. Regulations (`/regulamentos`)

List and view regulations documents.

**File:** `src/pages/Regulamentos.tsx`

**Features:**
- Search by title/description (client-side)
- Regulation cards grid
- Modal to open regulation files
- Fetches from: `GET /api/public/regulations`

**Data Display:**
- Title
- Description
- Category
- Created date
- File download via `file_url`

---

## Components

### Navigation

**Navbar** (`src/components/Navbar.tsx`)
- Logo
- Navigation links
- Responsive mobile menu

**Footer** (`src/components/Footer.tsx`)
- Copyright information
- Social links

### Cards

**TournamentCard** (`src/components/TournamentCard.tsx`)
- Props: `id`, `name`, `modality`, `epoca`, `icon`
- Flexbox layout with sticky footer
- Hover effects with color transitions
- Links to tournament detail page

**GameCard** (`src/components/GameCard.tsx`)
- Props: `title`, `team1`, `team2`, `modalidade`, `time`, `onClick`
- Display match information
- Click handler for opening modal

---

## Type System

All TypeScript types are centralized in `src/api/types.ts`:

### Core Types

```typescript
// Course
interface Course {
  id: string;
  name: string;
  abbreviation: string;
}

// Season
interface Season {
  id: string;
  year: number;
  display_name: string;
  is_active: boolean;
}

// Modality
interface Modality {
  id: string;
  name: string;
  type: string;
  description?: string;
}

// Match
interface Match {
  id: string;
  tournament_id: string;
  tournament_name: string;
  team_home: {
    id: string;
    name: string;
    course_abbreviation: string;
  };
  team_away: {
    id: string;
    name: string;
    course_abbreviation: string;
  };
  modality: {
    id: string;
    name: string;
  };
  start_time: string;
  location: string;
  status: 'scheduled' | 'in_progress' | 'finished' | 'cancelled';
  home_score?: number;
  away_score?: number;
}

// Tournament
interface TournamentPublicDetail {
  id: string;
  name: string;
  modality: {
    id: string;
    name: string;
  };
  season: {
    id: string;
    year: number;
    display_name: string;
  };
  status: string;
  rules?: string;
  start_date?: string;
  team_count: number;
  rankings?: TournamentRankingEntry[];
}

// Rankings
interface RankingEntry {
  position: number;
  course_id: number;
  course_name: string;
  course_short_code: string;
  points: number;
  played: number;
  won: number;
  drawn: number;
  lost: number;
}

// Regulation
interface Regulation {
  id: string;
  title: string;
  description?: string;
  category?: string;
  file_url: string;
  created_at: string;
  updated_at: string;
}
```

---

## API Integration Details

### General Patterns

**Loading States:**
```typescript
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

**Fetching Data:**
```typescript
useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.{module}.{method}();
      setState(data);
    } catch (err) {
      console.error('Error:', err);
      setError('Error message');
    } finally {
      setLoading(false);
    }
  };
  fetchData();
}, [dependencies]);
```

### Filtering Strategies

**Server-side filtering (Tournaments):**
- Filters applied via query parameters
- API returns filtered results
- Used when filters significantly reduce data size

**Client-side filtering (Calendar, Regulations):**
- Fetch all data once
- Apply filters in component
- Used for simple filters on small datasets

---

## Mock Data

The public API uses mock data for development. Current mock data includes:

### Seasons
- Season 1: 2024 (24/25)
- Season 2: 2025 (25/26) - Active

### Modalities
1. Futebol (id: 1)
2. Futsal (id: 2)
3. Andebol (id: 3)
4. Voleibol (id: 4)

### Courses/Núcleos
1. NEI (id: 1)
2. NEC (id: 2)
3. NET (id: 3)
4. NEMat (id: 4)
5. NEGeo (id: 5)

### Tournaments
- 5 tournaments across different modalities and seasons
- Each with unique rankings data

### Matches
- 16 matches total
- 4 finished matches (Nov 28, Nov 30, Dec 3) with scores
- 12 scheduled matches across December 2025 and January 2026
- Distributed across Dec 3, 7, 10, 14, 17, 21 and Jan 7, 11

### Regulations
- 5 regulations: Geral, Futsal, Futebol, Andebol, Minecraft
- Each with category, title, description

---

## Styling Guidelines

### Tailwind Classes

**Colors:**
- Primary: `teal-600`, `teal-500`, etc.
- Text: `gray-800` (headings), `gray-600` (body), `gray-500` (secondary)
- Backgrounds: `gray-50` (page), `white` (cards)

**Common Patterns:**

```css
/* Card */
bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-all

/* Button Primary */
px-6 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700

/* Input/Select */
w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-teal-500

/* Container */
max-w-6xl mx-auto py-8 px-4 md:px-8 lg:px-16
```

**Responsive Breakpoints:**
- `md:` - 768px and up
- `lg:` - 1024px and up

---

## Development

### Running the Frontend

```bash
cd src/frontend/public-website
npm install
npm run dev
```

The dev server will start on `http://localhost:5173`

### Building for Production

```bash
npm run build
```

Output in `dist/` directory.

### Environment Variables

Create `.env` file:
```
VITE_API_BASE_URL=http://localhost/api/public
```

---

## Known Limitations

1. **No Authentication**: Public website has no auth flow
2. **Mock Data**: Currently using mock data from public API
3. **Client-side Filtering**: Some pages fetch all data and filter client-side
4. **No Real-time Updates**: No WebSocket or polling for live match updates
5. **No Search**: Regulations search is local only

---

## Future Improvements

1. **Real Database Integration**: Replace mock data with actual DB queries
2. **Live Match Updates**: Add WebSocket for real-time score updates
3. **Advanced Search**: Server-side search for regulations and matches
4. **Caching**: Implement Redis caching for frequently accessed data
5. **Pagination**: Add pagination for large datasets
6. **Accessibility**: Improve ARIA labels and keyboard navigation
7. **PWA**: Make it a Progressive Web App
8. **SEO**: Add meta tags and SSR for better SEO
9. **Analytics**: Track page views and user interactions
10. **Error Boundaries**: Better error handling with React Error Boundaries

---

## Testing

Currently no automated tests. Recommended testing strategy:

1. **Unit Tests**: Jest + React Testing Library
2. **Integration Tests**: Test API client methods
3. **E2E Tests**: Playwright or Cypress
4. **Visual Regression**: Chromatic or Percy

---

## Deployment

The frontend is containerized with Docker:

**Dockerfile:** `src/frontend/public-website/Dockerfile`

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

Deployed via `docker-compose.yml` alongside other services.
