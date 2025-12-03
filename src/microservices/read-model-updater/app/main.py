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
    tags={"application": "read-model-updater", "job": "read-model-updater"},
    version="1",
)
logger = logging.getLogger("read-model-updater")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Register event handlers
rabbitmq_service = RabbitMQService(service_name="read-model-updater")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("Read Model Updater started")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
    logger.info("Read Model Updater stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Read Model Updater"}


@app.get("/models")
async def get_read_models(current_user: dict = Depends(verify_token)):
    """Get read models - requires authentication."""
    logger.info(f"Read models retrieved by {current_user.get('preferred_username')}")
    return {"models": []}
