import asyncio
import logging
from contextlib import asynccontextmanager

import logging_loki
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_messaging import rabbitmq_service

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
    # Start RabbitMQ event consumer
    asyncio.create_task(rabbitmq_service.start_consuming(queue_name="modalities-queue"))
    logger.info("Modalities Service started")
    yield
    # Disconnect from RabbitMQ on shutdown
    await rabbitmq_service.disconnect()
    logger.info("Modalities Service stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Modalities Service"}
