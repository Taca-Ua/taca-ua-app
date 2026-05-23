import os
import sys
import types

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)


class _LoggerStub:
    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None


class _RabbitMQStub:
    async def start_consuming(self):
        return None

    async def disconnect(self):
        return None


class _OutboxPublisherStub:
    async def start(self):
        return None

    async def stop(self):
        return None


def _install_test_stubs() -> None:
    if "prometheus_fastapi_instrumentator" not in sys.modules:
        prom_mod = types.ModuleType("prometheus_fastapi_instrumentator")

        class Instrumentator:
            def instrument(self, app):
                return self

            def expose(self, app):
                return self

        prom_mod.Instrumentator = Instrumentator
        sys.modules["prometheus_fastapi_instrumentator"] = prom_mod

    if "taca_logging" not in sys.modules:
        logging_mod = types.ModuleType("taca_logging")

        class StructlogMiddleware:
            def __init__(self, app, **kwargs):
                self.app = app

            async def __call__(self, scope, receive, send):
                await self.app(scope, receive, send)

        logging_mod.StructlogMiddleware = StructlogMiddleware
        sys.modules["taca_logging"] = logging_mod

    if "app.events" not in sys.modules:
        events_mod = types.ModuleType("app.events")
        events_mod.rabbitmq_service = _RabbitMQStub()
        sys.modules["app.events"] = events_mod

    if "app.logger" not in sys.modules:
        logger_mod = types.ModuleType("app.logger")
        logger_mod.logger = _LoggerStub()
        sys.modules["app.logger"] = logger_mod

    if "app.outbox_publisher" not in sys.modules:
        outbox_mod = types.ModuleType("app.outbox_publisher")
        outbox_mod.outbox_publisher = _OutboxPublisherStub()
        sys.modules["app.outbox_publisher"] = outbox_mod

    if "app.routes" not in sys.modules:
        routes_mod = types.ModuleType("app.routes")
        routes_mod.router = APIRouter()
        routes_mod.course_router = APIRouter()
        routes_mod.modality_router = APIRouter()
        routes_mod.modality_type_router = APIRouter()
        routes_mod.nucleo_router = APIRouter()
        routes_mod.regulation_router = APIRouter()
        routes_mod.staff_router = APIRouter()
        routes_mod.student_router = APIRouter()
        routes_mod.team_router = APIRouter()
        sys.modules["app.routes"] = routes_mod

    if "app.internal_controller" not in sys.modules:
        internal_mod = types.ModuleType("app.internal_controller")
        internal_mod.router = APIRouter()
        sys.modules["app.internal_controller"] = internal_mod

    if "app.rebuild_controller_sse" not in sys.modules:
        rebuild_mod = types.ModuleType("app.rebuild_controller_sse")
        rebuild_mod.router = APIRouter()
        sys.modules["app.rebuild_controller_sse"] = rebuild_mod


@pytest.fixture(scope="session")
def app():
    _install_test_stubs()
    import app.main as main_mod

    return main_mod.app


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c
