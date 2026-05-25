"""
Logging configuration for read-model-updater
"""

from taca_logging import configure_logging, get_logger

# Configure structured logging
configure_logging(
    service_name="read-model-updater",
    log_level="INFO",
)

# Export logger for use in other modules
logger = get_logger("read-model-updater")
