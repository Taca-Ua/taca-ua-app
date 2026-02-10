from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_logging import StructlogMiddleware

from .events import rabbitmq_service
from .logger import logger
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer
    await rabbitmq_service.start_consuming()
    logger.info("service_started", action="startup")
    yield
    # Shutdown: Disconnect RabbitMQ
    await rabbitmq_service.disconnect()
    logger.info("service_stopped", action="shutdown")


app = FastAPI(lifespan=lifespan)

# Add structured logging middleware
app.add_middleware(StructlogMiddleware)

Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint

# Include routers
app.include_router(router)


@app.get("/")
def read_root():
    return {"Service": "Ranking Service"}
