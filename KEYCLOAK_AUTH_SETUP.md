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

```yaml
# Keycloak Configuration
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=taca-ua
KEYCLOAK_CLIENT_ID=api-client
KEYCLOAK_CLIENT_SECRET=your-client-secret-here
```

For production, use:
```yaml
KEYCLOAK_URL=https://your-keycloak-domain.com
KEYCLOAK_REALM=taca-ua
KEYCLOAK_CLIENT_ID=api-client
KEYCLOAK_CLIENT_SECRET=secure-client-secret
```

### Keycloak Setup Steps

#### 1. Create Realm
- Log in to Keycloak Admin Console (http://localhost:8080/admin)
- Create a new realm named `taca-ua`

#### 2. Create Client
- Go to Clients → Create
- Client ID: `api-client`
- Client Protocol: `openid-connect`
- Access Type: `confidential`
- Valid Redirect URIs: `http://localhost/api/*`, `http://localhost/*`
- Enable: `Standard Flow Enabled`, `Service Accounts Enabled`

#### 3. Get Client Credentials
- Go to Clients → api-client → Credentials
- Copy the `Client Secret`
- Use in `KEYCLOAK_CLIENT_SECRET` environment variable

#### 4. Create Roles
- Go to Roles → Add Role
- Create roles: `admin`, `user`, `moderator`

#### 5. Create Users
- Go to Users → Add User
- Set username, email
- Set Password (non-temporary)
- Go to Role Mappings → Assign roles

#### 6. Configure Mappers (Optional)
- Go to Clients → api-client → Mappers
- Add Mapper to include roles in token claims:
  - Mapper Type: `User Realm Role`
  - Token Claim Name: `realm_access.roles`

## Frontend Integration

### Login Flow

The frontend (admin-panel and public-website) should:

1. Redirect to Keycloak login:
   ```
   https://your-keycloak-domain/realms/taca-ua/protocol/openid-connect/auth?
     client_id=api-client&
     response_type=code&
     redirect_uri=http://localhost:3000/callback&
     scope=openid profile email
   ```

2. Handle callback and exchange code for token

3. Store JWT token in localStorage/sessionStorage

4. Send token in all API requests:
   ```
   Authorization: Bearer <token>
   ```

### Example (TypeScript/React)
```typescript
const token = localStorage.getItem('access_token');

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

### Get Token (Development)
```bash
curl -X POST http://localhost:8080/realms/taca-ua/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=api-client" \
  -d "client_secret=your-client-secret" \
  -d "username=john.doe" \
  -d "password=password" \
  -d "grant_type=password"
```

### Test Protected Endpoint
```bash
TOKEN="access-token-from-above"
curl -H "Authorization: Bearer $TOKEN" http://localhost/api/matches
```

### Test Without Token (Should fail)
```bash
curl http://localhost/api/matches
# Returns: 403 Unauthorized
```

## Security Notes

- **Keep client secrets secure** - Never commit to repository
- **Use HTTPS in production** - Keycloak URLs should be https://
- **Token expiration** - Tokens expire (default ~5 min), use refresh tokens
- **Scope validation** - Keycloak can enforce fine-grained permissions via scopes
- **CORS** - Configure CORS properly for frontend access

## Troubleshooting

### Token validation fails
- Check `KEYCLOAK_URL` and `KEYCLOAK_REALM` are correct
- Verify Keycloak is running: `http://localhost:8080`
- Check JWKS endpoint: `http://localhost:8080/realms/taca-ua/protocol/openid-connect/certs`

### Role not enforced
- Verify role is assigned to user in Keycloak
- Check role name matches in decorator: `@require_role("admin")`
- Ensure mapper includes `realm_access.roles` in token

### CORS errors
- Add frontend URL to Keycloak client Valid Redirect URIs
- Configure CORS headers in Nginx or FastAPI

## References

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.0 / OpenID Connect](https://openid.net/connect/)
- [Authlib Documentation](https://docs.authlib.org/)
