# TACA Read Models

Shared SQLAlchemy models package for TACA-UA microservices.

## Overview

This package provides read-only access models for querying data from various microservice schemas and read/write models for the `public_read` schema views.

## Models

### Source Models (Read-Only)

These models provide read-only access to data from individual microservices:

- `Game` - matches.game schema
- `Result` - matches.result schema
- `Tournament` - tournaments.tournament schema
- `Modality` - modalities.modality schema
- `TeamRanking` - ranking.team_ranking schema

### View Models (Read/Write)

These models are used to update materialized views in the public_read schema:

- `GamesView` - public_read.games_view
- `TournamentView` - public_read.tournament_view
- `RankingView` - public_read.ranking_view

## Usage

### Installation

Add to your service's `requirements.txt`:

```
-e ../../shared/read-model-shared
```

### Importing

```python
from taca_models import (
    Base,
    Game,
    GameState,
    GamesView,
    Modality,
    RankingView,
    Result,
    TeamRanking,
    Tournament,
    TournamentView,
)
```

## Services Using This Package

- `read-model-updater` - Updates the public_read views by listening to events
- `public-api` - Queries the public_read views to serve data to clients

## Development

### Installing in Development Mode

```bash
cd src/shared/read-model-shared
pip install -e .
```

### Running Tests

```bash
pytest
```

## Notes

- The `Base` declarative base is shared across all models
- Migrations (Alembic) remain in the `read-model-updater` service as it's the only service that writes to these tables
- This package only defines the model structure, not the migration logic
