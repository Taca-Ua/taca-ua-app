"""
Logging configuration for matches-service
"""

import logging
import sys
import time
import uuid
from typing import Callable, Optional

import logging_loki
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.types import Processor

loogger = logging.getLogger(__name__)


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
        # if action != "list_metrics":  # Avoid logging Prometheus scrape requests
        # logger.info(
        #     "request_received",
        #     action=action,
        #     method=method,
        #     path=path,
        #     query_params=str(request.query_params) if request.query_params else None,
        # )

        # Track timing
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log response
            if action != "list_metrics":  # Avoid logging Prometheus scrape requests
                logger.info(
                    "request_completed",
                    extra={
                        "action": action,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                    },
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
                extra={
                    "action": action,
                    "error": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": duration_ms,
                },
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


def configure_logging(
    service_name: str,
    loki_url: str = "http://loki:3100/loki/api/v1/push",
    log_level: str = "INFO",
    additional_tags: Optional[dict[str, str]] = None,
) -> None:
    """
    Configure structured logging with Loki integration.

    Args:
        service_name: Name of the service (e.g., "modalities-service")
        loki_url: URL of the Loki instance
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        additional_tags: Additional tags to add to Loki logs
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Create Loki handler
    tags = {
        "application": service_name,
        "service": service_name,
        "job": service_name,
    }
    if additional_tags:
        tags.update(additional_tags)

    loki_handler = logging_loki.LokiHandler(
        url=loki_url,
        tags=tags,
        version="1",
    )

    # Configure structlog processors
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library root logger with JSON formatter for both handlers
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    # Add handlers to root logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Loki handler also needs the JSON formatter
    loki_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(loki_handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structlog logger instance.

    Args:
        name: Optional logger name (defaults to the calling module)

    Returns:
        A bound structlog logger
    """
    return structlog.get_logger(name)


# Configure structured logging
configure_logging(
    service_name="public-api",
    log_level="INFO",
)
