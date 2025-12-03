import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import logging_loki
from fastapi import FastAPI, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from taca_messaging.rabbitmq_service import RabbitMQService

from shared.auth import verify_token, verify_token_optional, get_username
from .routes import all_routers
# Add src directory to path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

<<<<<<< HEAD
=======
# Add src directory to path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.auth import verify_token, verify_token_optional, get_username
from .rabbitmq_utils import consume, produce
>>>>>>> 5b485845f7a2685576922cd49c1b4546fdcb65ab

# Logging setup
handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "public-api", "job": "public-api"},
    version="1",
)
logger = logging.getLogger("public-api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Register event handlers
rabbitmq_service = RabbitMQService(service_name="public-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("Public API started")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
    logger.info("Public API stopped")


app = FastAPI(
    title="Public Data API",
    description="Public read-only API for TACA competition data - no authentication required",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/public/docs",
    redoc_url="/api/public/redoc",
    openapi_url="/api/public/openapi.json",
)

# Include all routers
for router in all_routers:
    app.include_router(router)

# Prometheus metrics endpoint
Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Public API"}


@app.post("/send-event")
async def send_event(msg: str, current_user: dict = Depends(verify_token)):
    """Send event - requires authentication. User info is in current_user token."""
<<<<<<< HEAD
    await rabbitmq_service.publish_event("test.event", {"message": msg})
    username = get_username(current_user)
    logger.info(f"Event sent: {msg} by {username}")
    return {"status": "sent", "sent_by": username}

=======
    username = get_username(current_user)
    await produce("test-queue", {"message": msg, "sent_by": username})
    logger.info(f"Event sent: {msg} by {username}")
    return {"status": "sent", "sent_by": username}
>>>>>>> 5b485845f7a2685576922cd49c1b4546fdcb65ab
