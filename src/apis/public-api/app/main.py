"""
Public API for TACA competition data.

This API exposes read-only access to materialized views containing
aggregated competition data from multiple microservices.
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session
from taca_logging import StructlogMiddleware

from . import schemas
from .database import check_db_connection, get_db
from .logger import logger
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("service_starting", action="startup")

    # Check database connection
    if check_db_connection():
        logger.info("database_connected", status="success")
    else:
        logger.error("database_connection_failed", status="error")

    logger.info("service_started", status="ready")
    yield

    # Shutdown
    logger.info("service_stopped", action="shutdown")


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
        logger.info("health_check", status="healthy")
        return schemas.HealthResponse(
            status="healthy",
            service="Public API",
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error("health_check", status="unhealthy", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")
