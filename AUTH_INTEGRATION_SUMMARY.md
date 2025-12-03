# Keycloak Authentication - Integration Guide

## Summary of Changes

This implementation adds JWT-based authentication using Keycloak across all services in the Taca-UA project.

### What Was Added

#### 1. Dependencies
All `requirements.txt` files updated with:
- **FastAPI services**: `authlib==1.3.0`, `python-multipart==0.0.6`
- **Django service**: `djangorestframework-simplejwt==5.3.2`, `python-keycloak==3.8.0`

#### 2. Shared Auth Module
**Location**: `src/shared/auth.py`

Provides:
- `verify_token()` - Validates JWT tokens and extracts user claims
- `require_role(*roles)` - Decorator for role-based access control
- Helper functions to extract user info from tokens

#### 3. Updated Services
All FastAPI services now have:
- Authentication import from `shared.auth`
- Protected endpoints that require JWT tokens
- Example endpoints showing authenticated requests

**Services Updated**:
- `src/apis/public-api/app/main.py`
- `src/microservices/matches-service/app/main.py`
- `src/microservices/modalities-service/app/main.py`
- `src/microservices/ranking-service/app/main.py`
- `src/microservices/tournaments-service/app/main.py`
- `src/microservices/read-model-updater/app/main.py`

#### 4. Configuration Files
- `.env.example` - Updated with Keycloak environment variables
- `KEYCLOAK_AUTH_SETUP.md` - Complete setup and integration guide

#### 5. Reference Implementation
- `src/apis/competiotion-api/keycloak_example.py` - Django integration example

## How to Use

### 1. Set Environment Variables
```bash
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=taca-ua
KEYCLOAK_CLIENT_ID=api-client
KEYCLOAK_CLIENT_SECRET=your-secret
```

### 2. Access Protected Endpoints
All API endpoints now require a Bearer token:

```bash
# Get token from Keycloak
TOKEN=$(curl -X POST http://localhost:8080/realms/taca-ua/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=api-client" \
  -d "username=user" \
  -d "password=password" \
  -d "grant_type=password" | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" http://localhost/api/matches
```

### 3. Add Authentication to New Endpoints
```python
from fastapi import Depends
from shared.auth import verify_token, require_role

@app.get("/data")
async def get_data(current_user: dict = Depends(verify_token)):
    return {"user": current_user["sub"]}

@app.post("/admin")
@require_role("admin")
async def admin_action(current_user: dict = Depends(verify_token)):
    return {"status": "admin action"}
```

## Next Steps

1. **Configure Keycloak** (see `KEYCLOAK_AUTH_SETUP.md`)
   - Create realm, client, roles, users
   
2. **Implement Django Integration**
   - Use `keycloak_example.py` as reference
   - Configure Django settings with JWT authentication
   
3. **Update Frontend**
   - Implement Keycloak login redirect
   - Store and send JWT tokens with API requests
   
4. **Test Authentication**
   - Get token from Keycloak
   - Test protected endpoints
   - Test role-based access
   
5. **Production Setup**
   - Use HTTPS for Keycloak URL
   - Secure client secrets
   - Configure CORS properly

## Architecture

```
┌─────────────┐
│  Keycloak   │ Issues JWT tokens
└──────┬──────┘
       │
       │ /protocol/openid-connect/token
       │ /protocol/openid-connect/certs (JWKS)
       │
       ├──────────────────────┬──────────────────────┐
       │                      │                      │
    ┌──▼──────────┐  ┌──────▼────────┐  ┌───────▼──────┐
    │  FastAPI    │  │  FastAPI      │  │  Django      │
    │  Public API │  │  Microservices│  │  Competition │
    │             │  │               │  │  API         │
    │ Protected   │  │  Protected    │  │ Protected    │
    │ Endpoints   │  │  Endpoints    │  │ Endpoints    │
    └─────────────┘  └───────────────┘  └──────────────┘
         │                    │                 │
         └────────────────────┼─────────────────┘
                              │
                         ┌────▼────┐
                         │ Frontend │
                         │ + Token  │
                         └──────────┘
```

## Endpoint Status

### Public Endpoints (No Auth Required)
- `GET /` - Service info (all services)
- `GET /.metrics` - Prometheus metrics (if configured)

### Protected Endpoints (Auth Required)
- `POST /send-event` - Public API
- `GET /matches` - Matches Service
- `GET /modalities` - Modalities Service
- `GET /rankings` - Ranking Service
- `GET /tournaments` - Tournaments Service
- `GET /models` - Read Model Updater

## Security Checklist

- [ ] Set strong `KEYCLOAK_CLIENT_SECRET`
- [ ] Configure CORS for frontend domains
- [ ] Set `KEYCLOAK_URL` to HTTPS in production
- [ ] Create Keycloak realm and roles
- [ ] Create test users with appropriate roles
- [ ] Test token expiration and refresh flow
- [ ] Configure rate limiting on token endpoint
- [ ] Monitor failed authentication attempts

## Troubleshooting

### Services won't start
- Check `KEYCLOAK_URL` is accessible
- Verify Keycloak container is running
- Check firewall/network settings

### Authentication fails
- Verify token format: `Authorization: Bearer <token>`
- Check token hasn't expired
- Verify user has required role
- Check Keycloak realm name matches config

### CORS errors
- Add frontend URL to Keycloak client Valid Redirect URIs
- Configure CORS in Nginx or FastAPI middleware

See `KEYCLOAK_AUTH_SETUP.md` for detailed setup instructions.
