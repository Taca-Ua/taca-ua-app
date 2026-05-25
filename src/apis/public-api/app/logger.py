"""
Logging configuration for matches-service
"""

from taca_logging import configure_logging, get_logger

# Configure structured logging
configure_logging(
    service_name="public-api",
    log_level="INFO",
)

# Export logger for use in other modules
logger = get_logger("public-api")
