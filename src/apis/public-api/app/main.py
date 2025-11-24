from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging
import logging_loki
from prometheus_fastapi_instrumentator import Instrumentator
from .kafka_utils import consume, produce

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
async def send_event(msg: str):
    await produce("test-topic", msg)
    logger.info(f"Event sent: {msg}")
    return {"status": "sent"}
