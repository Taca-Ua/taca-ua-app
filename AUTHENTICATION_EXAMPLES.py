"""
Practical Examples for Using Keycloak Authentication in Taca-UA
"""

# ============================================================================
# EXAMPLE 1: Basic Protected Endpoint (FastAPI)
# ============================================================================

from fastapi import FastAPI, Depends
from shared.auth import verify_token, get_user_id, get_username

app = FastAPI()

@app.get("/profile")
async def get_profile(current_user: dict = Depends(verify_token)):
    """
    Get user's profile. Requires valid JWT token.
    
    Request:
        GET /profile
        Authorization: Bearer <token>
    
    Response:
        {
            "user_id": "uuid",
            "username": "john.doe",
            "email": "john@example.com"
        }
    """
    user_id = get_user_id(current_user)
    username = get_username(current_user)
    email = current_user.get("email")
    
    return {
        "user_id": user_id,
        "username": username,
        "email": email
    }


# ============================================================================
# EXAMPLE 2: Role-Based Access Control
# ============================================================================

from shared.auth import require_role, get_user_roles

@app.post("/admin/settings")
@require_role("admin")
async def update_admin_settings(current_user: dict = Depends(verify_token), settings: dict = None):
    """
    Update admin settings. Only 'admin' role can access.
    
    Request:
        POST /admin/settings
        Authorization: Bearer <admin_token>
        Content-Type: application/json
        {"theme": "dark", "language": "en"}
    
    Response:
        {"status": "updated", "user": "admin_user"}
    """
    username = get_username(current_user)
    return {"status": "updated", "user": username}


@app.post("/moderator/report")
@require_role("moderator", "admin")  # Both roles allowed
async def create_report(current_user: dict = Depends(verify_token), report: dict = None):
    """
    Create report. Accessible to 'moderator' or 'admin' roles.
    
    Request:
        POST /moderator/report
        Authorization: Bearer <moderator_or_admin_token>
        Content-Type: application/json
        {"reason": "inappropriate content"}
    
    Response:
        {"report_id": "uuid", "created_by": "moderator"}
    """
    user_id = get_user_id(current_user)
    return {"report_id": "new-uuid", "created_by": user_id}


# ============================================================================
# EXAMPLE 3: Extracting Token Claims
# ============================================================================

from shared.auth import verify_token, get_user_roles

@app.get("/my-tournaments")
async def my_tournaments(current_user: dict = Depends(verify_token)):
    """Get tournaments for current user."""
    user_id = get_user_id(current_user)
    username = get_username(current_user)
    email = current_user.get("email")
    roles = get_user_roles(current_user)
    
    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "roles": list(roles),
        "tournaments": [
            {"id": 1, "name": "Spring Tournament", "role": "organizer"},
            {"id": 2, "name": "Summer Cup", "role": "participant"}
        ]
    }


# ============================================================================
# EXAMPLE 4: Conditional Logic Based on Roles
# ============================================================================

from fastapi import HTTPException, status

@app.put("/tournament/{tournament_id}")
async def update_tournament(
    tournament_id: int,
    current_user: dict = Depends(verify_token),
    data: dict = None
):
    """
    Update tournament. Admin can update any, user only their own.
    """
    user_id = get_user_id(current_user)
    roles = get_user_roles(current_user)
    
    # Admin bypass
    if "admin" in roles:
        return {"updated": True, "tournament_id": tournament_id}
    
    # Regular user - verify ownership
    # (This is pseudocode - implement actual ownership check)
    tournament_owner = "some-user-id"  # Would fetch from DB
    
    if user_id != tournament_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tournaments"
        )
    
    return {"updated": True, "tournament_id": tournament_id}


# ============================================================================
# EXAMPLE 5: Optional Authentication
# ============================================================================

from shared.auth import verify_token_optional

@app.get("/public-tournament/{tournament_id}")
async def get_public_tournament(
    tournament_id: int,
    current_user: dict = Depends(verify_token_optional)
):
    """
    Get public tournament info. Auth is optional for analytics.
    """
    tournament_data = {
        "id": tournament_id,
        "name": "Public Tournament",
        "participants": 100
    }
    
    # Add extra info if user is authenticated
    if current_user:
        user_id = get_user_id(current_user)
        # Check if user is registered
        is_registered = True  # Would check database
        tournament_data["user_registered"] = is_registered
    else:
        tournament_data["user_registered"] = False
    
    return tournament_data


# ============================================================================
# EXAMPLE 6: Get Token (Testing)
# ============================================================================

"""
Development: Get a token from Keycloak for testing

Run in terminal:
    curl -X POST http://localhost:8080/realms/taca-ua/protocol/openid-connect/token \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      -d "client_id=api-client" \\
      -d "client_secret=your-client-secret" \\
      -d "username=john.doe" \\
      -d "password=john-password" \\
      -d "grant_type=password"

Response:
    {
      "access_token": "eyJhbGc...",
      "expires_in": 300,
      "refresh_expires_in": 1800,
      "refresh_token": "eyJhbGc...",
      "token_type": "Bearer"
    }

Use access_token in API calls:
    curl -H "Authorization: Bearer eyJhbGc..." http://localhost/api/profile
"""


# ============================================================================
# EXAMPLE 7: Frontend Usage (JavaScript/TypeScript)
# ============================================================================

"""
// Store token after login
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// Send with API requests
async function fetchAPI(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 401) {
    // Token expired, refresh it
    const newToken = await refreshToken();
    localStorage.setItem('access_token', newToken);
    // Retry request
    return fetchAPI(url, options);
  }
  
  return response;
}

// Usage
const profile = await fetchAPI('http://localhost/api/profile').then(r => r.json());
console.log(profile);
// { user_id: "...", username: "john.doe", email: "john@example.com" }
"""


# ============================================================================
# EXAMPLE 8: Integration with RabbitMQ Events
# ============================================================================

from shared.auth import get_username

@app.post("/matches/{match_id}/score")
async def update_match_score(
    match_id: int,
    current_user: dict = Depends(verify_token),
    score: dict = None
):
    """
    Update match score and publish event with user info.
    """
    username = get_username(current_user)
    user_id = get_user_id(current_user)
    
    # Publish to RabbitMQ
    event = {
        "type": "match_score_updated",
        "match_id": match_id,
        "score": score,
        "updated_by_user": user_id,
        "updated_by_username": username,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    # await produce("match-updates", event)
    
    return {"status": "updated", "event": event}


# ============================================================================
# EXAMPLE 9: Error Handling
# ============================================================================

"""
Common error responses:

401 Unauthorized - No token or invalid token
{
  "detail": "Invalid token: <error message>"
}

403 Forbidden - Valid token but insufficient permissions
{
  "detail": "Required roles: admin, moderator"
}

Example error handling in frontend:
    try {
      const response = await fetch('/api/admin', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.status === 401) {
        // Redirect to login
        window.location.href = '/login';
      } else if (response.status === 403) {
        // Show permission error
        alert('You do not have permission to access this');
      } else {
        return response.json();
      }
    } catch (error) {
      console.error('API error:', error);
    }
"""


# ============================================================================
# EXAMPLE 10: Creating Endpoints with Different Security Levels
# ============================================================================

@app.get("/api/health")
async def health_check():
    """No auth required - health checks should always work."""
    return {"status": "healthy"}


@app.get("/api/user/profile")
async def user_profile(current_user: dict = Depends(verify_token)):
    """User auth required - any authenticated user."""
    return {"profile": "data"}


@app.post("/api/admin/users")
@require_role("admin")
async def admin_create_user(current_user: dict = Depends(verify_token), user_data: dict = None):
    """Admin auth required - only users with admin role."""
    return {"created": True}


@app.delete("/api/superadmin/reset")
@require_role("superadmin")
async def superadmin_reset(current_user: dict = Depends(verify_token)):
    """Superadmin only - most restrictive."""
    return {"reset": True}
