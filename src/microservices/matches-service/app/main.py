from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_logging import StructlogMiddleware

from .events import rabbitmq_service
from .internal_controller import router as internal_router
from .logger import logger
from .outbox_publisher import outbox_publisher
from .routes import router
from .scheduler import match_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer, OutboxPublisher, and Match Status Scheduler
    await rabbitmq_service.start_consuming()
    await outbox_publisher.start()
    await match_scheduler.start()
    logger.info("service_started", action="startup")
    yield
    # Shutdown: Stop scheduler, disconnect RabbitMQ and stop OutboxPublisher
    await match_scheduler.stop()
    await outbox_publisher.stop()
    await rabbitmq_service.disconnect()
    logger.info("service_stopped", action="shutdown")


app = FastAPI(
    title="Matches Service",
    description="Microservice for managing matches",
    lifespan=lifespan,
)

# Add structured logging middleware
app.add_middleware(StructlogMiddleware)

Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint

# Include routers
app.include_router(router, tags=["matches"])
app.include_router(internal_router)


@app.get("/")
def read_root():
    return {"Service": "Matches Service"}
