"""
Django logging configuration for competition-api
"""

import structlog
from taca_logging.structlog_config import configure_logging

# Configure structured logging for Django
configure_logging(
    service_name="competition-api",
    log_level="INFO",
)


def get_logger(name=None):
    """Get a structlog logger instance"""
    return structlog.get_logger(name)
