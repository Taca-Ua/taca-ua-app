"""
Shared Keycloak authentication utilities for FastAPI services.
Provides JWT validation and role-based access control decorators.
"""

import os
from typing import Optional, Set
from functools import wraps
from datetime import datetime

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from authlib.jose import jwt


# Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "taca-ua")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "api-client")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

# Build Keycloak URLs
KEYCLOAK_ISSUER = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
KEYCLOAK_JWKS_URI = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

# Security scheme
security = HTTPBearer()

# Cache for JWKS (public keys)
_jwks_cache = None
_jwks_cache_time = None
_JWKS_CACHE_TTL = 3600  # 1 hour


async def get_jwks():
    """Fetch and cache Keycloak public keys (JWKS)."""
    global _jwks_cache, _jwks_cache_time
    
    now = datetime.now().timestamp()
    if _jwks_cache and _jwks_cache_time and (now - _jwks_cache_time) < _JWKS_CACHE_TTL:
        return _jwks_cache
    
    async with httpx.AsyncClient() as client:
        response = await client.get(KEYCLOAK_JWKS_URI)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_cache_time = now
        return _jwks_cache


async def verify_token(credentials = Depends(security)) -> dict:
    """
    Verify JWT token from Authorization header.
    Returns decoded token claims if valid, raises HTTPException otherwise.
    """
    token = credentials.credentials
    
    try:
        jwks = await get_jwks()
        # Decode and verify JWT
        claims = jwt.decode(
            token,
            jwks,
            claims_options={
                "verify_aud": False,  # Optional: verify audience if needed
                "verify_exp": True,
            }
        )
        
        # Verify issuer
        if claims.get("iss") != KEYCLOAK_ISSUER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return claims
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_token_optional(
    credentials = Depends(security)
) -> Optional[dict]:
    """
    Optionally verify JWT token. Returns claims if token provided and valid, None otherwise.
    """
    if not credentials:
        return None
    return await verify_token(credentials)


def require_role(*required_roles: str):
    """
    Decorator to enforce role-based access control.
    
    Usage:
        @app.get("/admin")
        @require_role("admin")
        async def admin_endpoint(current_user: dict = Depends(verify_token)):
            return {"message": "Admin only"}
        
        @app.get("/data")
        @require_role("admin", "user")
        async def data_endpoint(current_user: dict = Depends(verify_token)):
            return {"message": "Admin or user"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No user context",
                )
            
            # Check roles in token
            user_roles: Set[str] = set(current_user.get("realm_access", {}).get("roles", []))
            
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required roles: {', '.join(required_roles)}",
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_user_id(current_user: dict) -> Optional[str]:
    """Extract user ID (subject) from token claims."""
    return current_user.get("sub")


def get_user_roles(current_user: dict) -> Set[str]:
    """Extract roles from token claims."""
    return set(current_user.get("realm_access", {}).get("roles", []))


def get_user_email(current_user: dict) -> Optional[str]:
    """Extract email from token claims."""
    return current_user.get("email")


def get_username(current_user: dict) -> Optional[str]:
    """Extract username from token claims."""
    return current_user.get("preferred_username")
