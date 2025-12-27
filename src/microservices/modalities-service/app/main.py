from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .events import rabbitmq_service
from .logger import logger
from .outbox_publisher import outbox_publisher
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer and OutboxPublisher
    await rabbitmq_service.start_consuming()
    await outbox_publisher.start()
    logger.info("Modalities Service started")
    yield
    # Shutdown: Stop OutboxPublisher and disconnect RabbitMQ
    await outbox_publisher.stop()
    await rabbitmq_service.disconnect()
    logger.info("Modalities Service stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint

# Include routers
app.include_router(router, tags=["modalities", "teams", "students"])


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Modalities Service"}
