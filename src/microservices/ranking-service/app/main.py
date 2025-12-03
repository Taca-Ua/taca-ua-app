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

from shared.auth import verify_token

# Logging setup
handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "ranking-service", "job": "ranking-service"},
    version="1",
)
logger = logging.getLogger("ranking-service")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Register event handlers
rabbitmq_service = RabbitMQService(service_name="ranking-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("Ranking Service started")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
    logger.info("Ranking Service stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Ranking Service"}


@app.get("/rankings")
async def get_rankings(current_user: dict = Depends(verify_token)):
    """Get all rankings - requires authentication."""
    logger.info(f"Rankings retrieved by {current_user.get('preferred_username')}")
    return {"rankings": []}
