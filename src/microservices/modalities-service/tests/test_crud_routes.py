from __future__ import annotations

import importlib
import sys
import types
import uuid

import pytest
from fastapi import HTTPException


class _EventStub:
    @classmethod
    def create(cls, aggregate_id=None, data=None):
        return cls()

    def event_type(self):
        return self.__class__.__name__

    def aggregate_type(self):
        return "modality"

    def to_data_dict(self):
        return {}


class _DataStub:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _LoggerStub:
    def info(self, *args, **kwargs):
        return None


class _OutboxStub:
    def emit_event(self, *args, **kwargs):
        return None


class FakeModalityType:
    id = "id"

    def __init__(self, id=None):
        self.id = id or uuid.uuid4()


class FakeModality:
    id = "id"

    def __init__(self, name, modality_type_id, created_by, created_at, updated_at):
        self.id = uuid.uuid4()
        self.name = name
        self.modality_type_id = modality_type_id
        self.created_by = created_by
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "modality_type_id": self.modality_type_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class _DummyModel:
    id = "id"


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *_args, **_kwargs):
        return self

    def all(self):
        return self.items

    def first(self):
        return self.items[0] if self.items else None


class FakeDB:
    def __init__(self, modalities=None, modality_types=None):
        self.modalities = modalities or []
        self.modality_types = modality_types or []

    def query(self, model):
        if model is FakeModality:
            return FakeQuery(self.modalities)
        if model is FakeModalityType:
            return FakeQuery(self.modality_types)
        return FakeQuery([])

    def add(self, obj):
        if isinstance(obj, FakeModality):
            self.modalities.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, _obj):
        return None

    def delete(self, obj):
        if obj in self.modalities:
            self.modalities.remove(obj)

    def rollback(self):
        return None


@pytest.fixture
def routes_module(monkeypatch):
    events_pkg = types.ModuleType("taca_events")
    pyd_pkg = types.ModuleType("taca_events.pydantic_schemas")
    modalities_pkg = types.ModuleType("taca_events.pydantic_schemas.modalities")

    def _getattr(name):
        if name.endswith("Data"):
            return _DataStub
        return _EventStub

    modalities_pkg.__getattr__ = _getattr  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "taca_events", events_pkg)
    monkeypatch.setitem(sys.modules, "taca_events.pydantic_schemas", pyd_pkg)
    monkeypatch.setitem(
        sys.modules, "taca_events.pydantic_schemas.modalities", modalities_pkg
    )

    logger_mod = types.ModuleType("app.logger")
    logger_mod.logger = _LoggerStub()
    monkeypatch.setitem(sys.modules, "app.logger", logger_mod)

    db_mod = types.ModuleType("app.database")
    db_mod.get_db_session = lambda: None
    monkeypatch.setitem(sys.modules, "app.database", db_mod)

    outbox_mod = types.ModuleType("app.outbox_publisher")
    outbox_mod.outbox_publisher = _OutboxStub()
    monkeypatch.setitem(sys.modules, "app.outbox_publisher", outbox_mod)

    models_mod = types.ModuleType("app.models")
    models_mod.Modality = FakeModality
    models_mod.ModalityType = FakeModalityType
    models_mod.__getattr__ = lambda _name: _DummyModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "app.models", models_mod)

    sys.modules.pop("app.routes.modality_routes", None)
    return importlib.import_module("app.routes.modality_routes")


def test_create_read_update_delete_modality(routes_module):
    modality_type = FakeModalityType(id=uuid.uuid4())
    db = FakeDB(modality_types=[modality_type], modalities=[])

    created = routes_module.create_modality(
        routes_module.ModalityCreate(name="Futsal", modality_type_id=modality_type.id),
        db=db,
    )
    assert created["name"] == "Futsal"

    modality_id = db.modalities[0].id
    fetched = routes_module.get_modality(modality_id, db=db)
    assert fetched["id"] == modality_id

    updated = routes_module.update_modality(
        modality_id,
        routes_module.ModalityUpdate(name="Futsal Pro"),
        db=db,
    )
    assert updated["name"] == "Futsal Pro"

    routes_module.delete_modality(modality_id, db=db)
    assert db.modalities == []


def test_create_modality_without_type_returns_404(routes_module):
    db = FakeDB(modality_types=[], modalities=[])

    with pytest.raises(HTTPException) as exc:
        routes_module.create_modality(
            routes_module.ModalityCreate(
                name="Atletismo",
                modality_type_id=uuid.uuid4(),
            ),
            db=db,
        )

    assert exc.value.status_code == 404
