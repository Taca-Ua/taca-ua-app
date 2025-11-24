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
    tags={"application": "read-model-updater", "job": "read-model-updater"},
    version="1",
)
logger = logging.getLogger("read-model-updater")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume())
    logger.info("Read Model Updater started")
    yield
    logger.info("Read Model Updater stopped")

app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Read Model Updater"}
