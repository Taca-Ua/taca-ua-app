from __future__ import annotations

import importlib
import sys
import types
import uuid
from datetime import datetime, timezone
from enum import Enum

import pytest
from fastapi import HTTPException


class _EventStub:
    @classmethod
    def create(cls, aggregate_id=None, data=None):
        return cls()

    def event_type(self):
        return self.__class__.__name__

    def aggregate_type(self):
        return "match"

    def to_data_dict(self):
        return {}


class _DataStub:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _LoggerStub:
    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None


class _OutboxStub:
    def emit_event(self, *args, **kwargs):
        return None


class FakeMatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class FakeMatch:
    id = "id"
    tournament_id = "tournament_id"
    status = "status"

    def __init__(
        self,
        tournament_id=None,
        location="Loc",
        start_time=None,
        created_by=None,
        status=FakeMatchStatus.SCHEDULED,
    ):
        self.id = uuid.uuid4()
        self.tournament_id = tournament_id
        self.location = location
        self.start_time = start_time or datetime.now(timezone.utc)
        self.created_by = created_by or uuid.uuid4()
        self.status = status
        self.participants = []
        self.updated_at = None

    def to_dict(self, include_details=False):
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "location": self.location,
            "start_time": self.start_time,
            "status": (
                self.status.value if isinstance(self.status, Enum) else self.status
            ),
            "participants": [{"participant": p.participant} for p in self.participants],
            "created_by": self.created_by,
            "created_at": datetime.now(timezone.utc),
            "updated_at": self.updated_at,
        }


class FakeMatchParticipant:
    def __init__(self, match_id, participant):
        self.match_id = match_id
        self.participant = participant


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *_args, **_kwargs):
        return self

    def count(self):
        return len(self.items)

    def yield_per(self, _n):
        return self

    def all(self):
        return self.items

    def first(self):
        return self.items[0] if self.items else None


class FakeDB:
    def __init__(self, matches=None):
        self.matches = matches or []
        self._added = []

    def query(self, model):
        if model is FakeMatch:
            return FakeQuery(self.matches)
        if model is FakeMatchParticipant:
            participants = []
            for m in self.matches:
                participants.extend(m.participants)
            return FakeQuery(participants)
        return FakeQuery([])

    def add(self, obj):
        self._added.append(obj)
        if isinstance(obj, FakeMatch):
            self.matches.append(obj)
        if isinstance(obj, FakeMatchParticipant):
            for m in self.matches:
                if m.id == obj.match_id:
                    m.participants.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, _obj):
        return None

    def delete(self, obj):
        if obj in self.matches:
            self.matches.remove(obj)


@pytest.fixture
def routes_module(monkeypatch):
    events_pkg = types.ModuleType("taca_events")
    pyd_pkg = types.ModuleType("taca_events.pydantic_schemas")
    matches_pkg = types.ModuleType("taca_events.pydantic_schemas.matches")

    def _getattr(name):
        if name.endswith("Data"):
            return _DataStub
        return _EventStub

    matches_pkg.__getattr__ = _getattr  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "taca_events", events_pkg)
    monkeypatch.setitem(sys.modules, "taca_events.pydantic_schemas", pyd_pkg)
    monkeypatch.setitem(
        sys.modules, "taca_events.pydantic_schemas.matches", matches_pkg
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
    models_mod.Match = FakeMatch
    models_mod.MatchParticipant = FakeMatchParticipant
    models_mod.MatchStatus = FakeMatchStatus
    models_mod.Comment = type("Comment", (), {})
    models_mod.Lineup = type("Lineup", (), {})
    monkeypatch.setitem(sys.modules, "app.models", models_mod)

    sys.modules.pop("app.routes", None)
    return importlib.import_module("app.routes")


def test_create_read_update_delete_match(routes_module):
    db = FakeDB(matches=[])

    created = routes_module.create_match(
        routes_module.schemas.MatchCreate(
            tournament_id=None,
            location="Court A",
            start_time=datetime.now(timezone.utc),
            created_by=uuid.uuid4(),
            participants=[uuid.uuid4(), uuid.uuid4()],
        ),
        db=db,
    )

    assert created["location"] == "Court A"
    created_id = db.matches[0].id

    read_item = routes_module.get_match(created_id, db=db)
    assert read_item["id"] == created_id

    updated = routes_module.update_match(
        created_id,
        routes_module.schemas.MatchUpdate(location="Court B", status="in_progress"),
        db=db,
    )
    assert updated["location"] == "Court B"
    assert updated["status"] == "in_progress"

    routes_module.delete_match(created_id, db=db)
    assert db.matches == []


def test_get_match_not_found(routes_module):
    db = FakeDB(matches=[])
    with pytest.raises(HTTPException) as exc:
        routes_module.get_match(uuid.uuid4(), db=db)
    assert exc.value.status_code == 404
