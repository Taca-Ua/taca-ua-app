from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_logging import StructlogMiddleware

from .events import rabbitmq_service
from .logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("service_started", action="startup")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
    logger.info("service_stopped", action="shutdown")


app = FastAPI(
    title="Read Model Updater Service",
    description="Maintains materialized views for public read access",
    version="1.0.0",
    lifespan=lifespan,
)

# Add structured logging middleware
app.add_middleware(StructlogMiddleware)

Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint


@app.get("/")
def read_root():
    return {
        "service": "Read Model Updater",
        "version": "1.0.0",
        "description": "Maintains materialized views and provides read endpoints",
    }
