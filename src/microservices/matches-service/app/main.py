import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import logging_loki
from fastapi import FastAPI, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from taca_messaging.rabbitmq_service import RabbitMQService

# Add src directory to path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.auth import verify_token, require_role

from .routes import router
from .logger import logger
from .events import rabbitmq_service

# Logging setup
handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "matches-service", "job": "matches-service"},
    version="1",
)
logger = logging.getLogger("matches-service")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Register event handlers
rabbitmq_service = RabbitMQService(service_name="matches-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("Matches Service started")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
    logger.info("Matches Service stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint

# Include routers
app.include_router(router, tags=["matches"])


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Matches Service"}


@app.get("/matches")
async def get_matches(current_user: dict = Depends(verify_token)):
    """Get all matches - requires authentication."""
    logger.info(f"Matches retrieved by {current_user.get('preferred_username')}")
    return {"matches": []}
