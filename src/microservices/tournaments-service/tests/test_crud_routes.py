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
        return "tournament"

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


class FakeCompetitorType(str, Enum):
    TEAM = "team"
    ATHLETE = "athlete"


class FakeTournament:
    id = "id"
    status = "status"
    modality_id = "modality_id"

    def __init__(
        self,
        modality_id,
        name,
        start_date,
        status,
        scoring_format_id,
        competitor_type,
        created_by,
    ):
        self.id = uuid.uuid4()
        self.modality_id = modality_id
        self.name = name
        self.start_date = start_date
        self.status = status
        self.scoring_format_id = scoring_format_id
        self.competitor_type = competitor_type
        self.created_by = created_by
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = None
        self.finished_at = None
        self.finished_by = None
        self.competitors = []

    def to_dict(self, include_ranking=False):
        return {
            "id": self.id,
            "modality_id": self.modality_id,
            "name": self.name,
            "start_date": self.start_date,
            "status": self.status,
            "scoring_format_id": self.scoring_format_id,
            "competitor_type": (
                self.competitor_type.value
                if isinstance(self.competitor_type, Enum)
                else self.competitor_type
            ),
            "competitors": self.competitors,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "finished_at": self.finished_at,
            "finished_by": self.finished_by,
        }


class FakeTournamentCompetitor:
    tournament_id = "tournament_id"
    competitor_type = "competitor_type"
    team_id = "team_id"
    athlete_id = "athlete_id"


class FakeTournamentRankingPosition:
    tournament_id = "tournament_id"


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *_args, **_kwargs):
        return self

    def all(self):
        return self.items

    def first(self):
        return self.items[0] if self.items else None

    def delete(self):
        self.items.clear()


class FakeDB:
    def __init__(self, tournaments=None):
        self.tournaments = tournaments or []

    def query(self, model):
        if model is FakeTournament:
            return FakeQuery(self.tournaments)
        return FakeQuery([])

    def add(self, obj):
        if isinstance(obj, FakeTournament):
            self.tournaments.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, _obj):
        return None

    def delete(self, obj):
        if obj in self.tournaments:
            self.tournaments.remove(obj)

    def rollback(self):
        return None


@pytest.fixture
def routes_module(monkeypatch):
    events_pkg = types.ModuleType("taca_events")
    pyd_pkg = types.ModuleType("taca_events.pydantic_schemas")
    tournaments_pkg = types.ModuleType("taca_events.pydantic_schemas.tournaments")

    def _getattr(name):
        if name.endswith("Data"):
            return _DataStub
        return _EventStub

    tournaments_pkg.__getattr__ = _getattr  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "taca_events", events_pkg)
    monkeypatch.setitem(sys.modules, "taca_events.pydantic_schemas", pyd_pkg)
    monkeypatch.setitem(
        sys.modules, "taca_events.pydantic_schemas.tournaments", tournaments_pkg
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
    models_mod.CompetitorType = FakeCompetitorType
    models_mod.Tournament = FakeTournament
    models_mod.TournamentCompetitor = FakeTournamentCompetitor
    models_mod.TournamentRankingPosition = FakeTournamentRankingPosition
    monkeypatch.setitem(sys.modules, "app.models", models_mod)

    sys.modules.pop("app.routes", None)
    return importlib.import_module("app.routes")


@pytest.mark.asyncio
async def test_create_read_update_delete_tournament(routes_module):
    db = FakeDB(tournaments=[])

    payload = routes_module.TournamentCreate(
        modality_id=uuid.uuid4(),
        name="Open Cup",
        start_date=datetime.now(timezone.utc),
        competitor_type="team",
        scoring_format_id=uuid.uuid4(),
    )

    created = await routes_module.create_tournament(payload, db=db)
    assert created.name == "Open Cup"

    tournament_id = db.tournaments[0].id

    read_item = await routes_module.get_tournament(tournament_id, db=db)
    assert read_item.id == tournament_id

    updated = await routes_module.update_tournament(
        tournament_id,
        routes_module.TournamentUpdate(name="Open Cup 2", status="active"),
        db=db,
    )
    assert updated.name == "Open Cup 2"
    assert updated.status == "active"

    await routes_module.delete_tournament(tournament_id, db=db)
    assert db.tournaments == []


@pytest.mark.asyncio
async def test_get_tournament_not_found(routes_module):
    db = FakeDB(tournaments=[])
    with pytest.raises(HTTPException) as exc:
        await routes_module.get_tournament(uuid.uuid4(), db=db)
    assert exc.value.status_code == 404
