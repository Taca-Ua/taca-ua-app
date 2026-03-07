"""
TACA Logging - Shared structured logging configuration for all services
"""

from .structlog_config import configure_logging, get_logger

# FastAPI middleware is optional - only available if FastAPI is installed
try:
    from .fastapi_middleware import StructlogMiddleware

    __all__ = ["configure_logging", "get_logger", "StructlogMiddleware"]
except ImportError:
    # FastAPI not installed, only export core logging functions
    __all__ = ["configure_logging", "get_logger"]
