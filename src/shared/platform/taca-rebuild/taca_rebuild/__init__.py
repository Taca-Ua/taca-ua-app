"""
taca-rebuild — Generic rebuild orchestration framework for TACA-UA microservices.

Two rebuild strategies are available:

**HTTP Strategy** (load entire snapshot at once)::

    from taca_rebuild import BaseRebuildService, make_rebuild_router

**SSE Strategy** (stream data incrementally)::

    from taca_rebuild import BaseSSERebuildService, make_sse_rebuild_router


HTTP Implementation
===================

For smaller datasets, subclass :class:`BaseRebuildService` and implement:

- ``snapshot_sources`` — property returning ``{service_name: url}``
- ``clear_tables()`` — delete all rows that will be repopulated
- ``rebuild_from_snapshots(raw)`` — parse raw JSON and insert rows; return count
- ``get_status()`` — return a dict with current table row counts

Then wire up::

    router = make_rebuild_router(
        service_cls=MyRebuildService,
        rabbitmq_svc=rabbitmq_service,
        get_db=get_db_session,
        internal_token=Config.INTERNAL_API_TOKEN,
    )
    app.include_router(router)


SSE Implementation (recommended for large datasets)
===================================================

For large datasets, subclass :class:`BaseSSERebuildService` and implement:

- ``snapshot_sources`` — property returning ``{service_name: sse_stream_url}``
- ``clear_tables()`` — delete all rows that will be repopulated
- ``rebuild_from_snapshot_event(service_name, event)`` — process each event incrementally
- ``get_status()`` — return a dict with current table row counts

Then wire up::

    router = make_sse_rebuild_router(
        service_cls=MySSERebuildService,
        rabbitmq_svc=rabbitmq_service,
        get_db=get_db_session,
        internal_token=Config.INTERNAL_API_TOKEN,
    )
    app.include_router(router)
"""

from .dto import RebuildResult, SnapshotFetchError
from .fetcher import SnapshotFetcher
from .router import make_rebuild_router
from .service import BaseRebuildService
from .sse_fetcher import SSESnapshotFetcher
from .sse_router import make_sse_rebuild_router
from .sse_service import BaseSSERebuildService

__all__ = [
    # HTTP approach
    "BaseRebuildService",
    "make_rebuild_router",
    "SnapshotFetcher",
    # SSE approach
    "BaseSSERebuildService",
    "make_sse_rebuild_router",
    "SSESnapshotFetcher",
    # Shared
    "RebuildResult",
    "SnapshotFetchError",
]
