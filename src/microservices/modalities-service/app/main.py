import asyncio
import logging
from contextlib import asynccontextmanager

import logging_loki
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .rabbitmq_utils import consume

# Logging setup
handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "modalities-service", "job": "modalities-service"},
    version="1",
)
logger = logging.getLogger("modalities-service")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(consume())
    logger.info("Modalities Service started")
    yield
    logger.info("Modalities Service stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Modalities Service"}
