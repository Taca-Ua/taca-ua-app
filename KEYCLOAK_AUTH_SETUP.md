# Keycloak Authentication Setup Guide

## Overview
This project uses Keycloak as the identity provider for JWT-based authentication across all FastAPI microservices and the Django competition API.

## Architecture

```
Keycloak (Identity Provider)
    ↓
Issues JWT tokens
    ↓
Services validate tokens via public JWKS endpoint
    ↓
Role-based access control enforced per endpoint
```

## Configuration

### Environment Variables

Add these to your `docker-compose.yml` or `.env` file:

**For Frontend (Admin Panel):**
- No environment variables needed
- Configuration is in `src/frontend/admin-panel/src/auth/KeycloakProvider.tsx`:
  ```typescript
  url: 'http://localhost/keycloak',
  realm: 'taca-ua',
  clientId: 'api-client',
  ```

**For Backend APIs (Future Integration):**
```yaml
# Keycloak Configuration
KEYCLOAK_URL=http://keycloak:8080/keycloak  # Internal Docker URL
KEYCLOAK_REALM=taca-ua
KEYCLOAK_CLIENT_ID=api-client
# Note: Public clients don't need KEYCLOAK_CLIENT_SECRET
```

For production, use:
```yaml
KEYCLOAK_URL=https://your-keycloak-domain.com/keycloak
KEYCLOAK_REALM=taca-ua
KEYCLOAK_CLIENT_ID=api-client
```

### Keycloak Setup Steps

#### Option A: Automated Setup (PowerShell)

Run these commands to automatically set up Keycloak:

```powershell
# 1. Start services
docker-compose up -d

# Wait for Keycloak to be ready (~15 seconds)
Start-Sleep -Seconds 15

# 2. Get admin token
$adminToken = (Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/realms/master/protocol/openid-connect/token" -ContentType "application/x-www-form-urlencoded" -Body @{username="admin";password="admin";grant_type="password";client_id="admin-cli"}).access_token

# 3. Create realm
Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/admin/realms" -Headers @{Authorization="Bearer $adminToken";"Content-Type"="application/json"} -Body '{"realm":"taca-ua","enabled":true}'

# 4. Create public client with PKCE (for frontend)
Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/admin/realms/taca-ua/clients" -Headers @{Authorization="Bearer $adminToken";"Content-Type"="application/json"} -Body '{"clientId":"api-client","enabled":true,"publicClient":true,"directAccessGrantsEnabled":true,"standardFlowEnabled":true,"implicitFlowEnabled":false,"redirectUris":["http://localhost/admin/*","http://localhost/*"],"webOrigins":["*"],"attributes":{"pkce.code.challenge.method":"S256"}}'

# 5. Create roles
Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/admin/realms/taca-ua/roles" -Headers @{Authorization="Bearer $adminToken";"Content-Type"="application/json"} -Body '{"name":"admin_geral"}'
Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/admin/realms/taca-ua/roles" -Headers @{Authorization="Bearer $adminToken";"Content-Type"="application/json"} -Body '{"name":"admin_nucleo"}'

# 6. Create test user
Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/admin/realms/taca-ua/users" -Headers @{Authorization="Bearer $adminToken";"Content-Type"="application/json"} -Body '{"username":"testuser","enabled":true,"email":"testuser@example.com","credentials":[{"type":"password","value":"testpass123","temporary":false}]}'

# 7. Assign role to user
$userId = (Invoke-RestMethod -Method GET -Uri "http://localhost/keycloak/admin/realms/taca-ua/users?username=testuser" -Headers @{Authorization="Bearer $adminToken"})[0].id
$roleId = (Invoke-RestMethod -Method GET -Uri "http://localhost/keycloak/admin/realms/taca-ua/roles/admin_geral" -Headers @{Authorization="Bearer $adminToken"}).id
Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/admin/realms/taca-ua/users/$userId/role-mappings/realm" -Headers @{Authorization="Bearer $adminToken";"Content-Type"="application/json"} -Body "[{`"id`":`"$roleId`",`"name`":`"admin_geral`"}]"

Write-Host "✅ Keycloak setup complete!"
```

#### Option B: Manual Setup (Keycloak Admin Console)

1. **Access Admin Console**
   - Navigate to: http://localhost/keycloak/admin
   - Login with: `admin` / `admin`

2. **Create Realm**
   - Click dropdown in top-left → Create Realm
   - Realm name: `taca-ua`
   - Click Create

3. **Create Client (IMPORTANT: Public Client for Frontend)**
   - Go to Clients → Create Client
   - Client ID: `api-client`
   - Click Next
   - **Client authentication: OFF** (this makes it a public client)
   - **Standard flow: ON**
   - **Direct access grants: ON**
   - Click Save
   - Go to Settings tab:
     - Valid redirect URIs: `http://localhost/admin/*`, `http://localhost/*`
     - Valid post logout redirect URIs: `http://localhost/*`
     - Web origins: `*`
   - Go to Advanced tab → Advanced Settings:
     - Proof Key for Code Exchange Code Challenge Method: `S256`
   - Click Save

4. **Create Roles**
   - Go to Realm roles → Create role
   - Role name: `admin_geral` → Save
   - Create another role: `admin_nucleo` → Save

5. **Create User**
   - Go to Users → Add user
   - Username: `testuser`
   - Email: `testuser@example.com`
   - Email verified: ON
   - Click Create
   - Go to Credentials tab:
     - Set password: `testpass123`
     - Temporary: OFF
     - Click Set password
   - Go to Role mapping tab:
     - Click Assign role
     - Filter by realm roles
     - Select `admin_geral`
     - Click Assign

#### Important Configuration Notes

**⚠️ Client Type: PUBLIC vs CONFIDENTIAL**
- Frontend apps (React, Vue, etc.) **MUST** use **public** clients
- Public clients do not have a client secret
- Use PKCE (Proof Key for Code Exchange) for security
- Backend APIs can use confidential clients with secrets

**🔐 Security with PKCE**
- PKCE protects against authorization code interception
- Code Challenge Method: `S256` (SHA-256)
- Automatically handled by keycloak-js library

**🌐 CORS Configuration**
- Web Origins set to `*` allows all CORS requests
- For production, restrict to specific domains
- Example: `https://yourdomain.com`

## Frontend Integration

### Current Implementation Status

The admin-panel frontend **is already fully integrated** with Keycloak:
- ✅ `KeycloakProvider.tsx` - Context provider with auto-refresh
- ✅ `Login.tsx` - Login page with Keycloak redirect
- ✅ `ProtectedRoute.tsx` - Role-based route protection
- ✅ PKCE enabled (S256) for secure authentication
- ✅ Silent SSO check configured
- ✅ Automatic token refresh every 60 seconds

### Testing the Integration

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Access admin panel:**
   - Navigate to: http://localhost/admin
   - Click "Admin Geral" button

3. **Login with test credentials:**
   - Username: `testuser`
   - Password: `testpass123`

4. **Verify authentication:**
   - You should be redirected to `/geral/dashboard`
   - Open DevTools (F12) → Network tab
   - Check for `Authorization: Bearer eyJ...` headers

### Login Flow (OAuth2 Authorization Code Flow with PKCE)

1. User clicks "Admin Geral" button
2. Frontend redirects to Keycloak:
   ```
   http://localhost/keycloak/realms/taca-ua/protocol/openid-connect/auth?
     client_id=api-client&
     response_type=code&
     redirect_uri=http://localhost/admin/&
     scope=openid&
     code_challenge=<generated>&
     code_challenge_method=S256
   ```
3. User logs in at Keycloak page
4. Keycloak redirects back with authorization code
5. Frontend exchanges code for tokens (automatically by keycloak-js)
6. Tokens stored in React context (in-memory, not localStorage)
7. User redirected to dashboard based on roles

### Token Storage

**⚠️ Security Best Practice:**
- Tokens are stored **in-memory** (React state) only
- **NOT** in localStorage or sessionStorage
- This prevents XSS attacks from stealing tokens
- Tokens are lost on page refresh (user needs to re-authenticate)
- For persistent sessions, implement refresh token flow

### Implementation Example

The admin-panel uses this pattern (already implemented):

```typescript
// KeycloakProvider.tsx
const keycloak = new Keycloak({
  url: 'http://localhost/keycloak',
  realm: 'taca-ua',
  clientId: 'api-client',
});

// Initialize with PKCE
keycloak.init({
  onLoad: 'check-sso',
  pkceMethod: 'S256',
  silentCheckSsoRedirectUri: window.location.origin + '/admin/silent-check-sso.html',
  checkLoginIframe: false,
});

// Login function
const login = () => keycloak.login();

// Role check function  
const hasRole = (role: string) => keycloak.hasRealmRole(role);
```

### Adding API Requests with Auth

```typescript
// Example API call (pattern to implement in api/client.ts)
const token = keycloak.token;

const response = await fetch('http://localhost/api/matches', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## API Usage

### Protected Endpoint
```python
from fastapi import Depends
from shared.auth import verify_token, get_user_roles

@app.get("/data")
async def get_data(current_user: dict = Depends(verify_token)):
    user_id = current_user['sub']
    roles = current_user['realm_access']['roles']
    return {"user": user_id, "roles": roles}
```

### Role-Based Endpoint
```python
from shared.auth import require_role

@app.post("/admin/users")
@require_role("admin")
async def create_user(current_user: dict = Depends(verify_token), data: dict = None):
    # Only admins can create users
    return {"created": True}
```

## Token Claims

Example JWT payload decoded:
```json
{
  "sub": "user-id-uuid",
  "preferred_username": "john.doe",
  "email": "john@example.com",
  "email_verified": true,
  "realm_access": {
    "roles": ["user", "admin"]
  },
  "exp": 1704067200,
  "iat": 1704063600,
  "iss": "http://keycloak:8080/realms/taca-ua"
}
```

## Testing

### Test Login Flow (Browser)

1. Navigate to http://localhost/admin
2. Click "Admin Geral"
3. Login with `testuser` / `testpass123`
4. Should redirect to `/geral/dashboard`

### Get Token (Command Line - for API testing)

**PowerShell:**
```powershell
$response = Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/realms/taca-ua/protocol/openid-connect/token" -ContentType "application/x-www-form-urlencoded" -Body @{username="testuser";password="testpass123";grant_type="password";client_id="api-client"}
$token = $response.access_token
Write-Host "Token: $token"
```

**Bash:**
```bash
curl -X POST http://localhost/keycloak/realms/taca-ua/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=api-client" \
  -d "username=testuser" \
  -d "password=testpass123" \
  -d "grant_type=password"
```

### Test Protected Endpoint (when backend is integrated)
```bash
TOKEN="access-token-from-above"
curl -H "Authorization: Bearer $TOKEN" http://localhost/api/matches
```

### Decode JWT Token (inspect claims)

Visit https://jwt.io and paste your token to see:
- User ID (`sub`)
- Roles (`realm_access.roles`)
- Expiration (`exp`)
- Issuer (`iss`)

## Security Notes

- **Keep client secrets secure** - Never commit to repository
- **Use HTTPS in production** - Keycloak URLs should be https://
- **Token expiration** - Tokens expire (default ~5 min), use refresh tokens
- **Scope validation** - Keycloak can enforce fine-grained permissions via scopes
- **CORS** - Configure CORS properly for frontend access

## Troubleshooting

### "Keycloak init failed" Error
**Cause:** Client is configured as confidential instead of public

**Fix:**
1. Go to Keycloak Admin Console → Clients → api-client
2. Go to Settings tab
3. Set "Client authentication" to OFF
4. Save

Or run this PowerShell command:
```powershell
$adminToken = (Invoke-RestMethod -Method POST -Uri "http://localhost/keycloak/realms/master/protocol/openid-connect/token" -ContentType "application/x-www-form-urlencoded" -Body @{username="admin";password="admin";grant_type="password";client_id="admin-cli"}).access_token
$clients = Invoke-RestMethod -Method GET -Uri "http://localhost/keycloak/admin/realms/taca-ua/clients" -Headers @{Authorization="Bearer $adminToken"}
$apiClient = $clients | Where-Object { $_.clientId -eq "api-client" }
Invoke-RestMethod -Method PUT -Uri "http://localhost/keycloak/admin/realms/taca-ua/clients/$($apiClient.id)" -Headers @{Authorization="Bearer $adminToken";"Content-Type"="application/json"} -Body '{"clientId":"api-client","enabled":true,"publicClient":true,"directAccessGrantsEnabled":true,"standardFlowEnabled":true,"implicitFlowEnabled":false,"redirectUris":["http://localhost/admin/*","http://localhost/*"],"webOrigins":["*"],"attributes":{"pkce.code.challenge.method":"S256"}}'
```

### Frontend Stuck on "Loading..."
**Cause:** Keycloak initialization not completing

**Checks:**
1. Check browser console for errors (F12)
2. Verify Keycloak is running: http://localhost/keycloak
3. Verify realm exists: http://localhost/keycloak/realms/taca-ua
4. Check client is public (not confidential)

### Token validation fails
- Check `KEYCLOAK_URL` points to correct instance
- Verify Keycloak is running: `docker ps | grep keycloak`
- Check JWKS endpoint: `http://localhost/keycloak/realms/taca-ua/protocol/openid-connect/certs`
- Ensure backend uses internal URL: `http://keycloak:8080/keycloak` (not localhost)

### Role not enforced / User can't access dashboard
- Verify role is assigned to user in Keycloak Admin Console
- Check role name matches exactly: `admin_geral` (case-sensitive)
- Ensure role mapper includes `realm_access.roles` in token (default config)
- Decode JWT at https://jwt.io to verify roles are in token

### CORS errors in browser console
- Add frontend URL to Valid Redirect URIs: `http://localhost/admin/*`
- Set Web Origins to `*` (dev) or specific domain (production)
- Check Nginx CORS headers are configured (already done in nginx.conf.http)

### npm dependencies not installed in container
**Symptoms:** "Failed to resolve import 'keycloak-js'"

**Fix:**
```bash
docker exec taca-ua-app-admin-panel-1 npm install
docker restart taca-ua-app-admin-panel-1
```

Or rebuild:
```bash
docker-compose up -d --build admin-panel
```

## References

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.0 / OpenID Connect](https://openid.net/connect/)
- [Authlib Documentation](https://docs.authlib.org/)
