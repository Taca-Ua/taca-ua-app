"""
Django middleware for adding request context to structured logs
"""

import uuid

import structlog


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
