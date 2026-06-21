"""
Public API for TACA competition data.

This API exposes read-only access to materialized views containing
aggregated competition data from multiple microservices.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from . import schemas
from .cache import clear_redis_cache, get_cache_stats
from .database import check_db_connection, check_redis_connection, get_db
from .logger import StructlogMiddleware
from .routes import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("service_starting", extra={"action": "startup"})

    # Check database connection
    if check_db_connection():
        logger.info("database_connected", extra={"status": "success"})
    else:
        logger.error("database_connection_failed", extra={"status": "error"})

    # Initialize Redis cache
    if check_redis_connection():
        logger.info("redis_cache_initialized", extra={"status": "success"})
    else:
        logger.warning("redis_cache_unavailable", extra={"status": "disabled"})

    logger.info("service_started", extra={"status": "ready"})
    yield

    # Shutdown
    logger.info("service_stopped", extra={"action": "shutdown"})


app = FastAPI(
    title="Public Data API",
    description="Public read-only API for TACA competition data - no authentication required",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/public/docs",
    redoc_url="/api/public/redoc",
    openapi_url="/api/public/openapi.json",
)

# Add structured logging middleware
app.add_middleware(StructlogMiddleware)

# Include API routes
app.include_router(router)

# Prometheus metrics endpoint
Instrumentator().instrument(app).expose(app)


# ==================== Health & Root ====================


@app.get("/", response_model=schemas.HealthResponse)
def read_root():
    """Root endpoint with service information."""
    return schemas.HealthResponse(
        status="healthy",
        service="Public API",
        timestamp=datetime.utcnow(),
    )


@app.get("/health", response_model=schemas.HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Verifies that the API is running and can connect to the database.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        logger.info("health_check", extra={"status": "healthy"})
        return schemas.HealthResponse(
            status="healthy",
            service="Public API",
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error("health_check", extra={"error": str(e), "status": "unhealthy"})
        raise HTTPException(status_code=503, detail="Service unavailable")


# ==================== Cache Management Endpoints ====================


@app.get("/cache/stats")
def get_cache_statistics():
    """
    Get Redis cache statistics.

    Returns cache status, memory usage, and performance metrics.
    """
    stats = get_cache_stats()
    logger.info("cache_stats_requested", extra={"stats": stats})
    return {"cache": stats}


@app.post("/cache/clear")
def clear_cache():
    """
    Clear all Redis cache entries.

    **Warning**: This will clear all cached data and force database hits until cache is repopulated.
    Use with caution.
    """
    try:
        clear_redis_cache()
        logger.info("cache_cleared_by_admin", extra={"action": "manual_clear"})
        return {
            "status": "success",
            "message": "Cache cleared successfully",
        }
    except Exception as e:
        logger.error("cache_clear_failed", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Failed to clear cache")
