from __future__ import annotations

import importlib
import sys
import types
import uuid

import pytest
from fastapi import HTTPException


class _LoggerStub:
    def warning(self, *args, **kwargs):
        return None


class FakeEscalao:
    modality_type_id = "modality_type_id"

    def __init__(self, name, min_participants, max_participants, points):
        self.name = name
        self.min_participants = min_participants
        self.max_participants = max_participants
        self.points = points


class FakeTournament:
    tournament_id = "tournament_id"

    def __init__(self, tournament_id, scoring_format_id):
        self.tournament_id = tournament_id
        self.scoring_format_id = scoring_format_id


class FakeTournamentCompetitor:
    tournament_id = "tournament_id"


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items

    def count(self):
        return len(self.items)


class FakeDB:
    def __init__(self, routes_module, tournament=None, competitors=None, escaloes=None):
        self.routes_module = routes_module
        self.tournament = tournament
        self.competitors = competitors or []
        self.escaloes = escaloes or []

    def query(self, model):
        if model is self.routes_module.Tournament:
            return FakeQuery([self.tournament] if self.tournament else [])
        if model is self.routes_module.TournamentCompetitor:
            return FakeQuery(self.competitors)
        if model is self.routes_module.ModalityTypeEscalao:
            return FakeQuery(self.escaloes)
        return FakeQuery([])


@pytest.fixture
def routes_module(monkeypatch):
    db_mod = types.ModuleType("app.database")
    db_mod.get_db_session = lambda: None
    monkeypatch.setitem(sys.modules, "app.database", db_mod)

    logger_mod = types.ModuleType("app.logger")
    logger_mod.logger = _LoggerStub()
    monkeypatch.setitem(sys.modules, "app.logger", logger_mod)

    models_mod = types.ModuleType("app.models")
    models_mod.ModalityTypeEscalao = FakeEscalao
    models_mod.Tournament = FakeTournament
    models_mod.TournamentCompetitor = FakeTournamentCompetitor
    monkeypatch.setitem(sys.modules, "app.models", models_mod)

    sys.modules.pop("app.routes", None)
    return importlib.import_module("app.routes")


def test_calculate_tournament_tier_returns_expected_rank(routes_module):
    db = FakeDB(
        routes_module,
        escaloes=[FakeEscalao("Gold", 4, 10, [10, 8, 6])],
    )

    result = routes_module.calculate_tournament_tier(
        routes_module.schemas.TournamentTierCalculationRequest(
            tournament_id=str(uuid.uuid4()),
            modality_type_id=str(uuid.uuid4()),
            participant_count=6,
        ),
        db=db,
    )

    assert result.rank == "Gold"
    assert result.points == [10, 8, 6]


def test_get_tournament_tier_not_found(routes_module):
    db = FakeDB(routes_module, tournament=None)

    with pytest.raises(HTTPException) as exc:
        routes_module.get_tournament_tier(uuid.uuid4(), db=db)

    assert exc.value.status_code == 404
