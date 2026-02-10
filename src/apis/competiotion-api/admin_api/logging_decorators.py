"""
Logging decorators for Django views
"""

import functools
import time
from typing import Callable

import structlog
from rest_framework.request import Request
from rest_framework.response import Response


def log_action(action: str = None):
    """
    Decorator to add structured logging to Django REST Framework views

    Usage:
        @log_action("list_modalities")
        def get(self, request):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger
            logger = structlog.get_logger()

            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # Determine action name
            action_name = action
            if not action_name:
                # Auto-generate from function name and method
                method = request.method if request else "UNKNOWN"
                action_name = f"{method.lower()}_{func.__name__}"

            # Bind context
            context = {
                "action": action_name,
                "method": request.method if request else "UNKNOWN",
                "path": request.path if request else "UNKNOWN",
            }

            # Add path parameters from kwargs
            for key, value in kwargs.items():
                if key.endswith("_id"):
                    context[key] = str(value)

            # Log request
            logger.info("request_received", **context)

            # Track timing
            start_time = time.time()

            try:
                # Execute view function
                result = func(*args, **kwargs)

                # Calculate duration
                duration_ms = round((time.time() - start_time) * 1000, 2)

                # Log response
                status_code = (
                    result.status_code if isinstance(result, Response) else 200
                )
                logger.info(
                    "request_completed",
                    action=action_name,
                    status_code=status_code,
                    duration_ms=duration_ms,
                )

                return result

            except Exception as e:
                # Calculate duration
                duration_ms = round((time.time() - start_time) * 1000, 2)

                # Log error
                logger.error(
                    "request_failed",
                    action=action_name,
                    error=type(e).__name__,
                    error_message=str(e),
                    duration_ms=duration_ms,
                )
                raise

        return wrapper

    return decorator
