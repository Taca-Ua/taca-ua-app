from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .routes import router
from .logger import logger
from .events import rabbitmq_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("Ranking Service started")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
    logger.info("Ranking Service stopped")


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint

# Include routers
app.include_router(router)


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"Service": "Ranking Service"}
