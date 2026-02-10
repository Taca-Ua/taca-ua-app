"""
Logging configuration for ranking-service
"""

from taca_logging import configure_logging, get_logger

# Configure structured logging
configure_logging(
    service_name="ranking-service",
    log_level="INFO",
)

# Export logger for use in other modules
logger = get_logger("ranking-service")
