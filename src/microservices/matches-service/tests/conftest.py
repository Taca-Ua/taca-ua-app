import os
import sys
import types

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)


def _install_test_stubs() -> None:
    """Install lightweight module stubs for optional runtime dependencies.
    This lets tests import the FastAPI app without requiring infra packages.
    """

    if "prometheus_fastapi_instrumentator" not in sys.modules:
        prom_mod = types.ModuleType("prometheus_fastapi_instrumentator")

        class Instrumentator:  # pragma: no cover - simple test stub
            def instrument(self, app):
                return self

            def expose(self, app):
                return self

        prom_mod.Instrumentator = Instrumentator
        sys.modules["prometheus_fastapi_instrumentator"] = prom_mod

    if "taca_logging" not in sys.modules:
        logging_mod = types.ModuleType("taca_logging")

        class StructlogMiddleware:  # pragma: no cover - simple test stub
            def __init__(self, app, **kwargs):
                self.app = app

            async def __call__(self, scope, receive, send):
                await self.app(scope, receive, send)

        class _TestLogger:  # pragma: no cover - simple test stub
            def info(self, *args, **kwargs):
                return None

            def warning(self, *args, **kwargs):
                return None

            def error(self, *args, **kwargs):
                return None

        def configure_logging(*args, **kwargs):
            return None

        def get_logger(*args, **kwargs):
            return _TestLogger()

        logging_mod.StructlogMiddleware = StructlogMiddleware
        logging_mod.configure_logging = configure_logging
        logging_mod.get_logger = get_logger
        sys.modules["taca_logging"] = logging_mod

    if "taca_messaging" not in sys.modules:
        msg_mod = types.ModuleType("taca_messaging")

        class RabbitMQService:  # pragma: no cover - simple test stub
            def __init__(self, service_name: str):
                self.service_name = service_name

            async def start_consuming(self):
                return None

            async def disconnect(self):
                return None

        msg_mod.RabbitMQService = RabbitMQService
        sys.modules["taca_messaging"] = msg_mod

    if "taca_outbox" not in sys.modules:
        outbox_mod = types.ModuleType("taca_outbox")

        class OutboxPublisher:  # pragma: no cover - simple test stub
            def __init__(self, **kwargs):
                pass

            async def start(self):
                return None

            async def stop(self):
                return None

        outbox_mod.OutboxPublisher = OutboxPublisher
        sys.modules["taca_outbox"] = outbox_mod

    # Stub service routers to keep startup tests isolated from domain deps.
    from fastapi import APIRouter

    if "app.routes" not in sys.modules:
        routes_mod = types.ModuleType("app.routes")
        routes_mod.router = APIRouter()
        sys.modules["app.routes"] = routes_mod

    if "app.internal_controller" not in sys.modules:
        internal_mod = types.ModuleType("app.internal_controller")
        internal_mod.router = APIRouter()
        sys.modules["app.internal_controller"] = internal_mod

    if "app.outbox_publisher" not in sys.modules:
        outbox_service_mod = types.ModuleType("app.outbox_publisher")

        class _OutboxPublisherStub:  # pragma: no cover - simple test stub
            async def start(self):
                return None

            async def stop(self):
                return None

        outbox_service_mod.outbox_publisher = _OutboxPublisherStub()
        sys.modules["app.outbox_publisher"] = outbox_service_mod


@pytest.fixture(scope="session")
def app():
    """Import the FastAPI app and patch external async services to no-ops.
    This avoids connecting to RabbitMQ or starting the outbox publisher during tests.
    """
    # Import inside the fixture so test runner can control import timing
    _install_test_stubs()

    import app.events as events
    import app.main as main_mod
    import app.outbox_publisher as outbox

    async def _noop(*args, **kwargs):
        return None

    # Patch async start/stop methods used in the app lifespan
    if hasattr(events, "rabbitmq_service"):
        events.rabbitmq_service.start_consuming = _noop
        events.rabbitmq_service.disconnect = _noop
    if hasattr(outbox, "outbox_publisher"):
        outbox.outbox_publisher.start = _noop
        outbox.outbox_publisher.stop = _noop

    return main_mod.app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c
