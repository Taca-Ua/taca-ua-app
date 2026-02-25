import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_logging import StructlogMiddleware, configure_logging, get_logger
from taca_messaging.rabbitmq_service import RabbitMQService

from .routes import all_routers

# Add src directory to path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Configure structured logging
configure_logging(
    service_name="public-api",
    log_level="INFO",
)
logger = get_logger("public-api")

# Register event handlers
rabbitmq_service = RabbitMQService(service_name="public-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("service_started", action="startup")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
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

# Include all routers
for router in all_routers:
    app.include_router(router)

# Prometheus metrics endpoint
Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    return {"Service": "Public API"}


@app.post("/api/public/send-event")
async def send_event(msg: str):
    """Send event - public endpoint for testing."""
    await rabbitmq_service.publish_event("test.event", {"message": msg})
    logger.info(f"Event sent: {msg}")
    return {"status": "sent", "message": msg}
