from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .events import rabbitmq_service
from .logger import logger
from .outbox_publisher import outbox_publisher
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer and outbox publisher
    await rabbitmq_service.start_consuming()
    await outbox_publisher.start()
    logger.info("Tournaments Service started")
    yield
    # Shutdown: Disconnect RabbitMQ and stop outbox publisher
    await outbox_publisher.stop()
    await rabbitmq_service.disconnect()
    logger.info("Tournaments Service stopped")


app = FastAPI(
    title="Tournaments Service",
    description="Microservice for managing tournaments",
    version="1.0.0",
    lifespan=lifespan,
)
Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint

# Include routers
app.include_router(router, tags=["tournaments"])


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Tournaments Service", "version": "1.0.0"}
