import logging
from contextlib import asynccontextmanager

import logging_loki
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_messaging.rabbitmq_service import RabbitMQService

from .routes import all_routers

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
async def send_event(msg: str):
    await rabbitmq_service.publish_event("test.event", {"message": msg})
    logger.info(f"Event sent: {msg}")
    return {"status": "sent"}
