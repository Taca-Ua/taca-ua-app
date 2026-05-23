"""
Structlog configuration for TACA services with Loki integration
"""

import logging
import sys
from typing import Optional

import logging_loki
import structlog
from structlog.types import Processor


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
