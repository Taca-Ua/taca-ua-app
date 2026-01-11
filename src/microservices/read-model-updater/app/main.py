from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_logging import StructlogMiddleware, configure_logging, get_logger
from taca_messaging.rabbitmq_service import RabbitMQService

# Configure structured logging
configure_logging(
    service_name="read-model-updater",
    log_level="INFO",
)
logger = get_logger("read-model-updater")

# Register event handlers
rabbitmq_service = RabbitMQService(service_name="read-model-updater")


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


@app.get("/")
def read_root():
    return {"Service": "Read Model Updater"}
