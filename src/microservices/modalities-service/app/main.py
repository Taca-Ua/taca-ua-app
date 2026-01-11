from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_logging import StructlogMiddleware

from .events import rabbitmq_service
from .logger import logger
from .outbox_publisher import outbox_publisher
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start RabbitMQ consumer and OutboxPublisher
    await rabbitmq_service.start_consuming()
    await outbox_publisher.start()
    logger.info("service_started", action="startup")
    yield
    # Shutdown: Stop OutboxPublisher and disconnect RabbitMQ
    await outbox_publisher.stop()
    await rabbitmq_service.disconnect()
    logger.info("service_stopped", action="shutdown")


app = FastAPI(lifespan=lifespan)

# Add structured logging middleware
app.add_middleware(StructlogMiddleware)

Instrumentator().instrument(app).expose(app)  # Prometheus metrics endpoint

# Include routers
app.include_router(router, tags=["modalities", "teams", "students"])


@app.get("/")
def read_root():
    return {"Service": "Modalities Service"}
