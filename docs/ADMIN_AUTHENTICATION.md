# Admin Panel Authentication System

## Overview
This document describes the simple authentication system implemented for the TACA-UA admin panel. The system is designed for **Núcleo Administrators** to securely access and manage only their own núcleo's data (members, teams, and matches).

## Authentication Flow

### 1. Login Process
1. User navigates to `/admin/login/nucleo`
2. User enters username and password
3. Frontend sends credentials to `/api/admin/auth/login`
4. Backend validates credentials against mock user database
5. Backend returns session token and user info (including `course_id`)
6. Frontend stores token and user info in localStorage
7. User is redirected to `/admin/nucleo/dashboard`

### 2. Protected Routes
- All nucleo admin routes are wrapped with `ProtectedRoute` component
- Component checks if user is authenticated before rendering
- Redirects to login page if not authenticated
- Shows loading spinner while checking authentication state

### 3. Data Filtering
- All API endpoints filter data by the authenticated user's `course_id`
- Teams: Only teams belonging to user's núcleo
- Students: Only students enrolled in user's núcleo
- Matches: Only matches involving user's núcleo teams (home or away)

### 4. Logout Process
1. User clicks "Logout" button in sidebar
2. Frontend calls `/api/admin/auth/logout` endpoint
3. Backend invalidates session token
4. Frontend clears localStorage
5. User is redirected to login page

## Backend Implementation

### Mock Users Database
Located in `/src/apis/competiotion-api/admin_api/views/auth.py`

Available test accounts:
```
Username: admin_mect    | Password: password123 | Núcleo: MECT (course_id: 1)
Username: admin_lei     | Password: password123 | Núcleo: LEI (course_id: 2)
Username: admin_leci    | Password: password123 | Núcleo: LECI (course_id: 3)
Username: admin_biomed  | Password: password123 | Núcleo: BIOMED (course_id: 4)
Username: admin_mmat    | Password: password123 | Núcleo: MMAT (course_id: 5)
```

### Authentication Endpoints

#### POST /api/admin/auth/login
Login for nucleo administrators.

**Request:**
```json
{
  "username": "admin_mect",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "token": "session_1_admin_mect",
  "user": {
    "id": 1,
    "username": "admin_mect",
    "email": "admin@mect.ua.pt",
    "course_id": 1,
    "course_abbreviation": "MECT",
    "full_name": "João Silva"
  }
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

#### GET /api/admin/auth/me
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "admin_mect",
  "email": "admin@mect.ua.pt",
  "course_id": 1,
  "course_abbreviation": "MECT",
  "full_name": "João Silva"
}
```

**Error Response (401):**
```json
{
  "error": "Missing or invalid authorization header"
}
```

#### POST /api/admin/auth/logout
Logout current user and invalidate session token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204):**
No content

### Data Filtering Implementation

#### Teams Endpoint (GET /api/admin/teams)
**Filter Logic:**
```python
filtered_teams = [
    team for team in all_teams
    if team["course_id"] == user["course_id"]
]
```

**Example:** User with `course_id: 1` (MECT) will only see:
- Team 1: MECT Futebol A
- Team 3: MECT Futsal
- Team 4: MECT Andebol

#### Students Endpoint (GET /api/admin/students)
**Filter Logic:**
```python
filtered_students = [
    student for student in all_students
    if student["course_id"] == user["course_id"]
]
```

**Example:** User with `course_id: 1` (MECT) will only see students enrolled in MECT.

#### Matches Endpoint (GET /api/admin/matches)
**Filter Logic:**
```python
# Get team IDs for this nucleo
nucleo_team_ids = [
    team["id"] for team in teams
    if team["course_id"] == user["course_id"]
]

# Filter matches where either home or away team belongs to this nucleo
filtered_matches = [
    match for match in all_matches
    if match["team_home_id"] in nucleo_team_ids
    or match["team_away_id"] in nucleo_team_ids
]
```

**Example:** User with `course_id: 1` (MECT) will see matches where:
- Home team is MECT team OR
- Away team is MECT team

### Helper Function
`get_authenticated_user(request)` - Returns user dict or None if not authenticated.

Used in all protected views to:
1. Verify authentication
2. Get user's `course_id` for filtering
3. Return 401 if not authenticated

## Frontend Implementation

### Authentication Context
**File:** `/src/frontend/admin-panel/src/contexts/AuthContext.tsx`

**State:**
- `user`: Current user object or null
- `token`: Session token or null
- `isAuthenticated`: Boolean flag
- `isLoading`: Loading state during initialization

**Methods:**
- `login(username, password)`: Authenticate user
- `logout()`: Clear session and redirect

**Storage:**
- Token stored in: `localStorage.getItem('auth_token')`
- User info stored in: `localStorage.getItem('auth_user')`

### Protected Route Component
**File:** `/src/frontend/admin-panel/src/components/ProtectedRoute.tsx`

**Behavior:**
- Shows loading spinner while checking auth state
- Redirects to `/login/nucleo` if not authenticated
- Renders children if authenticated

### Login Page
**File:** `/src/frontend/admin-panel/src/pages/nucleo/LoginNucleo.tsx`

**Features:**
- Username and password inputs
- Loading state during login
- Error message display
- Automatic redirect on success

### API Client
**File:** `/src/frontend/admin-panel/src/api/client.ts`

**Features:**
- Base class for all API calls
- Automatic token injection via `Authorization: Bearer <token>`
- Error handling with typed responses
- Methods: GET, POST, PUT, DELETE

### API Modules

#### Teams API
**File:** `/src/frontend/admin-panel/src/api/teams.ts`

**Methods:**
- `getAll()`: Get all teams for current núcleo
- `create(data)`: Create new team
- `update(teamId, data)`: Update team
- `delete(teamId)`: Delete team

#### Students API
**File:** `/src/frontend/admin-panel/src/api/students.ts`

**Methods:**
- `getAll()`: Get all students for current núcleo
- `create(data)`: Create new student
- `update(studentId, data)`: Update student

#### Matches API
**File:** `/src/frontend/admin-panel/src/api/matches.ts`

**Methods:**
- `getAll()`: Get all matches for current núcleo
- `create(data)`: Create new match
- `update(matchId, data)`: Update match
- `submitResult(matchId, data)`: Submit match result
- `submitLineup(matchId, data)`: Submit lineup
- `addComment(matchId, data)`: Add comment
- `getMatchSheet(matchId)`: Download match sheet PDF

### Sidebar/Navbar
**File:** `/src/frontend/admin-panel/src/components/nucleo_navbar.tsx`

**Features:**
- Displays logged-in user info (name + núcleo abbreviation)
- Logout button with proper context cleanup
- Navigation links to protected pages

## Security Considerations

### Current Implementation (Development)
⚠️ **This is a MOCK authentication system for development purposes.**

**Current Security:**
- ✅ Session tokens track user sessions
- ✅ Data is filtered by `course_id`
- ✅ All admin endpoints require authentication
- ❌ Passwords stored in plain text
- ❌ Sessions stored in memory (lost on restart)
- ❌ No token expiration
- ❌ No HTTPS enforcement
- ❌ No rate limiting
- ❌ No CSRF protection

### Production Recommendations

For production deployment, replace with:

1. **Authentication Service**: Integrate with Keycloak or similar
2. **Password Hashing**: Use bcrypt or Argon2
3. **Database Sessions**: Store in PostgreSQL or Redis
4. **Token Expiration**: Implement JWT with refresh tokens
5. **HTTPS Only**: Enforce SSL/TLS
6. **Rate Limiting**: Prevent brute force attacks
7. **CSRF Tokens**: Protect state-changing operations
8. **Audit Logging**: Track all authentication events
9. **2FA Support**: Optional two-factor authentication
10. **Password Policy**: Enforce strong passwords

## Testing

### Manual Testing Steps

#### 1. Test Login
```bash
# Start Docker environment
docker compose -f docker-compose.dev.yml up -d

# Navigate to admin panel
http://localhost/admin/login/nucleo

# Try login with valid credentials
Username: admin_mect
Password: password123

# Should redirect to dashboard
```

#### 2. Test Data Filtering
```bash
# Login as admin_mect (course_id: 1)
# Check teams endpoint
curl -H "Authorization: Bearer session_1_admin_mect" \
  http://localhost/api/admin/teams

# Should return only MECT teams (course_id: 1)
# Expected: Teams 1, 3, 4

# Login as admin_lei (course_id: 2)
# Should return only LEI teams (course_id: 2)
# Expected: Teams 2, 6
```

#### 3. Test Protected Routes
```bash
# Without authentication, try to access dashboard
http://localhost/admin/nucleo/dashboard

# Should redirect to /admin/login/nucleo
```

#### 4. Test Logout
```bash
# Click logout button in sidebar
# Should clear localStorage
# Should redirect to login page
```

### Automated Testing (Future)

Recommended test coverage:
- Unit tests for auth context
- Integration tests for login flow
- E2E tests for protected routes
- API tests for data filtering

## Environment Variables

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost/api/admin
```

### Backend (Django settings)
```python
# Already configured in settings.py
DEBUG = True  # Set to False in production
ALLOWED_HOSTS = ["localhost", "competition-api"]
```

## Migration Path to Production

### Phase 1: Database Integration
1. Replace mock users with database queries
2. Implement proper User model
3. Add password hashing (bcrypt)

### Phase 2: Session Management
4. Use Django sessions or JWT
5. Implement token expiration
6. Add refresh token mechanism

### Phase 3: Security Hardening
7. Add HTTPS enforcement
8. Implement CSRF protection
9. Add rate limiting
10. Enable security headers

### Phase 4: External Authentication
11. Integrate with Keycloak
12. Implement OAuth2 flow
13. Add SSO support
14. Enable 2FA

## Troubleshooting

### Issue: "Authentication required" on all requests
**Solution:** Check that token is stored in localStorage and Authorization header is sent.

### Issue: User can see other núcleo's data
**Solution:** Verify that `get_authenticated_user()` is called in view and `course_id` filtering is applied.

### Issue: Token persists after logout
**Solution:** Ensure `localStorage.removeItem()` is called for both 'auth_token' and 'auth_user'.

### Issue: "Invalid credentials" on correct password
**Solution:** Check that username matches exactly (case-sensitive).

### Issue: Redirect loop on login
**Solution:** Verify AuthProvider is wrapping RouterProvider in main.tsx.

## Files Modified/Created

### Backend
- ✅ `/src/apis/competiotion-api/admin_api/views/auth.py` - NEW
- ✅ `/src/apis/competiotion-api/admin_api/serializers/auth.py` - NEW
- ✅ `/src/apis/competiotion-api/admin_api/views/__init__.py` - UPDATED
- ✅ `/src/apis/competiotion-api/admin_api/serializers/__init__.py` - UPDATED
- ✅ `/src/apis/competiotion-api/admin_api/urls.py` - UPDATED
- ✅ `/src/apis/competiotion-api/admin_api/views/teams.py` - UPDATED
- ✅ `/src/apis/competiotion-api/admin_api/views/students.py` - UPDATED
- ✅ `/src/apis/competiotion-api/admin_api/views/matches.py` - UPDATED

### Frontend
- ✅ `/src/frontend/admin-panel/src/contexts/AuthContext.tsx` - NEW
- ✅ `/src/frontend/admin-panel/src/components/ProtectedRoute.tsx` - NEW
- ✅ `/src/frontend/admin-panel/src/api/client.ts` - NEW
- ✅ `/src/frontend/admin-panel/src/api/teams.ts` - NEW
- ✅ `/src/frontend/admin-panel/src/api/students.ts` - NEW
- ✅ `/src/frontend/admin-panel/src/api/matches.ts` - NEW
- ✅ `/src/frontend/admin-panel/.env` - NEW
- ✅ `/src/frontend/admin-panel/src/main.tsx` - UPDATED
- ✅ `/src/frontend/admin-panel/src/pages/nucleo/LoginNucleo.tsx` - UPDATED
- ✅ `/src/frontend/admin-panel/src/routes/index.tsx` - UPDATED
- ✅ `/src/frontend/admin-panel/src/components/nucleo_navbar.tsx` - UPDATED

### Documentation
- ✅ `/docs/ADMIN_AUTHENTICATION.md` - NEW (this file)

## Next Steps

Now that authentication is implemented, the next steps are:

1. **Connect Admin Pages to API**: Update Membros, Equipas, and Jogos pages to use the API clients
2. **Add CRUD Operations**: Implement create, update, delete functionality in UI
3. **Add Form Validation**: Client-side validation for all forms
4. **Add Loading States**: Show spinners while fetching data
5. **Add Error Handling**: Display user-friendly error messages
6. **Test All Flows**: Verify all CRUD operations work correctly
7. **Add Dashboard Stats**: Connect dashboard cards to real data
8. **Implement Modality Management**: For general admin interface

## Summary

✅ **Backend**: Mock authentication system with session tokens and data filtering by `course_id`
✅ **Frontend**: Auth context, protected routes, login page, and API clients
✅ **Security**: Basic token-based auth (development only)
✅ **Testing**: Manual testing steps documented
⏳ **Next**: Connect admin pages to API and implement CRUD operations
