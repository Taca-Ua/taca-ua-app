"""
Django middleware for adding request context to structured logs and JWT validation.
"""

import logging
import uuid

import jwt
import structlog
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JWKS client — instantiated lazily so settings are fully loaded before use.
# ---------------------------------------------------------------------------
_jwks_client: jwt.PyJWKClient | None = None


def _get_jwks_client() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(
            settings.KEYCLOAK_JWKS_URI,
            cache_keys=True,
            lifespan=3600,  # re-fetch keys at most every hour
        )
    return _jwks_client


class KeycloakJWTMiddleware:
    """
    Middleware that validates Keycloak-issued JWTs on every request.

    Behaviour
    ---------
    * If ``DEV_AUTH_BYPASS_ENABLED=true`` and the request carries the header
      ``X-Dev-Auth-Token: <DEV_AUTH_BYPASS_TOKEN>`` the JWT check is **skipped**
      entirely.  ``request.user_id`` is set to ``"dev-bypass-user"`` and
      ``request.roles`` is set to the value of ``DEV_AUTH_BYPASS_ROLES``
      (comma-separated string, defaults to ``"general_admin"``).
      **Never enable this in production.**
    * If the ``Authorization: Bearer <token>`` header is **present**:
      - A valid token → ``request.user_id`` and ``request.roles`` are set.
      - An invalid/expired token → **401 Unauthorized** is returned immediately.
    * If the header is **absent** → ``request.user_id = None``, ``request.roles = []``
      and processing continues.  Individual views / decorators enforce authentication.
    * Paths listed in ``settings.KEYCLOAK_EXEMPT_PATHS`` are always skipped.

    Extracted claims
    ----------------
    * ``sub``                        → ``request.user_id``
    * ``realm_access.roles``         → ``request.roles``  (list of strings)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_paths: list[str] = getattr(settings, "KEYCLOAK_EXEMPT_PATHS", [])
        if any(request.path.startswith(p) for p in exempt_paths):
            request.user_id = None
            request.roles = []
            return self.get_response(request)

        auth_header: str = request.META.get("HTTP_AUTHORIZATION", "")

        # -------------------------------------------------------------------
        # DEV AUTH BYPASS — controlled by environment variables only.
        # Enable with:  DEV_AUTH_BYPASS_ENABLED=true
        #               DEV_AUTH_BYPASS_TOKEN=<any-secret-string>
        #               DEV_AUTH_BYPASS_ROLES=general_admin,nucleo_admin  (optional)
        # Then pass the header:  X-Dev-Auth-Token: <secret-string>
        # -------------------------------------------------------------------
        if not auth_header and getattr(settings, "DEV_AUTH_BYPASS_ENABLED", False):
            request.user_id = (
                "00000000-0000-0000-0000-000000000000"  # dummy UUID for dev bypass
            )
            request.roles = getattr(
                settings, "DEV_AUTH_BYPASS_ROLES", ["general_admin"]
            )
            logger.warning(
                "DEV AUTH BYPASS active for path %s — do NOT use in production",
                request.path,
            )
            return self.get_response(request)

        if not auth_header.startswith("Bearer "):
            # No token provided — unauthenticated request; views decide what to do.
            request.user_id = None
            request.roles = []
            return self.get_response(request)

        token = auth_header[len("Bearer ") :]
        try:
            payload = self._validate_token(token)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidAudienceError:
            return JsonResponse({"error": "Invalid token audience"}, status=401)
        except jwt.InvalidIssuerError:
            return JsonResponse({"error": "Invalid token issuer"}, status=401)
        except jwt.InvalidTokenError as exc:
            logger.warning("JWT validation failed: %s", exc)
            return JsonResponse(
                {"error": "Invalid token", "detail": str(exc)}, status=401
            )
        except Exception as exc:  # network errors, JWKS fetch failures, etc.
            logger.error("Unexpected error during JWT validation: %s", exc)
            return JsonResponse({"error": "Token validation failed"}, status=401)

        request.user_id = payload.get("sub")
        request.roles = payload.get("realm_access", {}).get("roles", [])

        return self.get_response(request)

    @staticmethod
    def _validate_token(token: str) -> dict:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)

        decode_kwargs: dict = {
            "algorithms": getattr(settings, "KEYCLOAK_ALGORITHMS", ["RS256"]),
            "options": {
                "verify_exp": True,
                "verify_iss": settings.KEYCLOAK_VALIDATE_ISSUER,
            },
            "issuer": settings.KEYCLOAK_ISSUER,
        }
        print(token, flush=True)
        print("JWT Decode kwargs:", decode_kwargs, flush=True)

        audience = getattr(settings, "KEYCLOAK_AUDIENCE", None)
        if audience:
            decode_kwargs["audience"] = audience
        else:
            decode_kwargs["options"]["verify_aud"] = False

        return jwt.decode(token, signing_key.key, **decode_kwargs)


class StructlogMiddleware:
    """Middleware to bind request context to structlog"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate request ID if not present
        request_id = request.META.get("HTTP_X_REQUEST_ID", str(uuid.uuid4()))

        # Bind request context to all logs in this request
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.path,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        try:
            response = self.get_response(request)
            return response
        finally:
            # Clear context after request
            structlog.contextvars.clear_contextvars()
