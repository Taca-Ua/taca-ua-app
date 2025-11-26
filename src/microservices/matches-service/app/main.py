import logging
from contextlib import asynccontextmanager

import logging_loki
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_messaging.rabbitmq_service import RabbitMQService

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


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Matches Service"}
