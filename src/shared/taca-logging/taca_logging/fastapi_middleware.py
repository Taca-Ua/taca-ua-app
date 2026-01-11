"""
FastAPI middleware for automatic request/response logging with structlog
"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class StructlogMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log all requests and responses with structured logging"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Extract action from path and method
        path = request.url.path
        method = request.method
        action = self._extract_action(path, method)

        # Bind request context
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=method,
            path=path,
            action=action,
        )

        # Log request
        logger = structlog.get_logger()
        logger.info(
            "request_received",
            action=action,
            method=method,
            path=path,
            query_params=str(request.query_params) if request.query_params else None,
        )

        # Track timing
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log response
            logger.info(
                "request_completed",
                action=action,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log error
            logger.error(
                "request_failed",
                action=action,
                error=type(e).__name__,
                error_message=str(e),
                duration_ms=duration_ms,
            )
            raise

        finally:
            # Clear context
            structlog.contextvars.clear_contextvars()

    def _extract_action(self, path: str, method: str) -> str:
        """Extract action name from path and method"""
        # Remove leading/trailing slashes
        path = path.strip("/")

        # Split path into parts
        parts = path.split("/")

        # Handle empty path (root)
        if not parts or parts[0] == "":
            return "root"

        # Get resource name (first part)
        resource = parts[0].replace("-", "_")

        # Determine operation based on method and path structure
        if method == "GET":
            if len(parts) == 1:
                return f"list_{resource}"
            else:
                return f"get_{resource.rstrip('s')}"  # Remove plural 's'
        elif method == "POST":
            return f"create_{resource.rstrip('s')}"
        elif method == "PUT" or method == "PATCH":
            return f"update_{resource.rstrip('s')}"
        elif method == "DELETE":
            return f"delete_{resource.rstrip('s')}"

        return f"{method.lower()}_{resource}"
