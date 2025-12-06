from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .events import rabbitmq_service
from .logger import logger
from .routes import router


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

# Include routers
app.include_router(router, tags=["matches"])


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Matches Service"}
