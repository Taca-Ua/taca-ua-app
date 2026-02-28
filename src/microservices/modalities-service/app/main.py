import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from taca_logging import StructlogMiddleware

from .events import rabbitmq_service
from .internal_controller import router as internal_router
from .logger import logger
from .outbox_publisher import outbox_publisher
from .routes import (
    course_router,
    modality_router,
    modality_type_router,
    nucleo_router,
    staff_router,
    student_router,
    team_router,
)

# Add src directory to path for shared module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


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
app.include_router(course_router, tags=["courses"])
app.include_router(modality_router, tags=["modalities"])
app.include_router(modality_type_router, tags=["modality_types"])
app.include_router(nucleo_router, tags=["nucleos"])
app.include_router(staff_router, tags=["staff"])
app.include_router(student_router, tags=["students"])
app.include_router(team_router, tags=["teams"])
app.include_router(internal_router)


@app.get("/")
def read_root():
    return {"Service": "Modalities Service"}


@app.get("/modalities")
async def get_modalities():
    """Get all modalities - internal microservice endpoint."""
    logger.info("Modalities retrieved")
    return {"modalities": []}
