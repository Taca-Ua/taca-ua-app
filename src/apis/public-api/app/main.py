import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import logging_loki
from fastapi import FastAPI, Depends
from prometheus_fastapi_instrumentator import Instrumentator

# Add src directory to path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.auth import verify_token, verify_token_optional, get_username
from .rabbitmq_utils import consume, produce

# Logging setup
handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "public-api", "job": "public-api"},
    version="1",
)
logger = logging.getLogger("public-api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Kafka consumer in background
    asyncio.create_task(consume())
    logger.info("Public API started")
    yield
    # Shutdown logic if needed
    logger.info("Public API stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Public API"}


@app.post("/send-event")
async def send_event(msg: str, current_user: dict = Depends(verify_token)):
    """Send event - requires authentication. User info is in current_user token."""
    username = get_username(current_user)
    await produce("test-queue", {"message": msg, "sent_by": username})
    logger.info(f"Event sent: {msg} by {username}")
    return {"status": "sent", "sent_by": username}
