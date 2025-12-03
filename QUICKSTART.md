# Quick Start: Keycloak Authentication

## 5-Minute Setup

### 1. Keycloak Configuration (Admin)
```bash
# Access Keycloak Admin Console
http://localhost:8080/admin

# Login with: admin / admin (from .env.example)

# Create realm: taca-ua
# Create client: api-client
# Copy client secret
```

### 2. Environment Setup
```bash
# Update docker-compose or .env
KEYCLOAK_CLIENT_SECRET=<paste-secret-from-step-1>
```

### 3. Install Dependencies
```bash
# All requirements.txt files already updated with:
# - authlib==1.3.0
# - python-multipart==0.0.6

pip install -r requirements.txt
```

### 4. Get a Test Token
```bash
curl -X POST http://localhost:8080/realms/taca-ua/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=api-client&client_secret=YOUR_SECRET&username=testuser&password=testpass&grant_type=password"
```

### 5. Test Protected Endpoint
```bash
export TOKEN="eyJhbGc..." # from step 4

curl -H "Authorization: Bearer $TOKEN" http://localhost/api/matches
# Expected: {"matches": []}
```

**Done!** 🎉 Authentication is working.

---

## Common Tasks

### Create New Protected Endpoint
```python
from fastapi import Depends
from shared.auth import verify_token

@app.get("/my-endpoint")
async def my_endpoint(current_user: dict = Depends(verify_token)):
    user_id = current_user["sub"]
    return {"data": "value", "user": user_id}
```

### Require Admin Role
```python
from shared.auth import require_role

@app.post("/admin-only")
@require_role("admin")
async def admin_endpoint(current_user: dict = Depends(verify_token)):
    return {"admin": True}
```

### Extract User Info
```python
from shared.auth import verify_token, get_username, get_user_roles

@app.get("/user-info")
async def user_info(current_user: dict = Depends(verify_token)):
    username = get_username(current_user)
    roles = get_user_roles(current_user)
    email = current_user.get("email")
    
    return {"username": username, "roles": list(roles), "email": email}
```

### Make Endpoint Public (No Auth)
```python
@app.get("/health")
async def health():
    return {"status": "ok"}  # No Depends(verify_token)
```

---

## Endpoints Reference

| Service | Endpoint | Public? | Role | Example |
|---------|----------|---------|------|---------|
| public-api | `POST /send-event` | ❌ | user | `curl -H "Auth: Bearer $TOKEN" -X POST http://localhost/api/send-event?msg=hello` |
| matches-service | `GET /matches` | ❌ | user | `curl -H "Auth: Bearer $TOKEN" http://localhost/api/matches` |
| modalities-service | `GET /modalities` | ❌ | user | `curl -H "Auth: Bearer $TOKEN" http://localhost/api/modalities` |
| ranking-service | `GET /rankings` | ❌ | user | `curl -H "Auth: Bearer $TOKEN" http://localhost/api/rankings` |
| tournaments-service | `GET /tournaments` | ❌ | user | `curl -H "Auth: Bearer $TOKEN" http://localhost/api/tournaments` |
| read-model-updater | `GET /models` | ❌ | user | `curl -H "Auth: Bearer $TOKEN" http://localhost/api/models` |

All services: `GET /` - ✅ Public (no auth needed)

---

## Troubleshooting

### "Invalid token issuer"
**Problem**: Keycloak URL mismatch
**Solution**: Verify `KEYCLOAK_URL` matches exactly in token and service

### "No module named shared"
**Problem**: Service can't find shared auth module
**Solution**: Check `sys.path` insertion in service main.py points to src/

### Token expires quickly
**Problem**: Token expires in 5 minutes (default)
**Solution**: Use refresh token or increase TTL in Keycloak

### CORS blocked
**Problem**: Frontend can't access API
**Solution**: Add frontend URL to Keycloak client Valid Redirect URIs

### Services won't start
**Problem**: Keycloak not accessible
**Solution**: Check `docker ps`, verify Keycloak container running on port 8080

---

## File Reference

| File | Purpose |
|------|---------|
| `src/shared/auth.py` | Core authentication logic |
| `KEYCLOAK_AUTH_SETUP.md` | Detailed setup guide |
| `AUTH_INTEGRATION_SUMMARY.md` | Integration overview |
| `AUTHENTICATION_EXAMPLES.py` | 10 practical examples |
| `IMPLEMENTATION_SUMMARY.md` | Complete documentation |

---

## Token Structure
```json
{
  "sub": "user-id-uuid",
  "preferred_username": "john.doe",
  "email": "john@example.com",
  "realm_access": {
    "roles": ["user", "admin"]
  },
  "exp": 1704067200,
  "iat": 1704063600
}
```

Use in code:
```python
user_id = current_user["sub"]
username = current_user["preferred_username"]
roles = current_user["realm_access"]["roles"]
email = current_user["email"]
```

---

## Frontend Example (React)
```jsx
// Login
const response = await fetch(`${KEYCLOAK_URL}/realms/taca-ua/protocol/openid-connect/token`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    client_id: 'api-client',
    username: email,
    password: password,
    grant_type: 'password'
  })
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);

// API Call
const data = await fetch('http://localhost/api/matches', {
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
}).then(r => r.json());
```

---

## Next Steps

1. **Read** `KEYCLOAK_AUTH_SETUP.md` for complete setup
2. **Review** `AUTHENTICATION_EXAMPLES.py` for code patterns
3. **Test** with curl before integrating frontend
4. **Implement** frontend login flow
5. **Deploy** with HTTPS for production

---

**Need help?** See KEYCLOAK_AUTH_SETUP.md → Troubleshooting section
