"""
taca-rebuild — Generic rebuild orchestration framework for TACA-UA microservices.

Public API::

    from taca_rebuild import BaseRebuildService, make_rebuild_router, RebuildResult

To implement a new rebuild service:

1. Subclass :class:`BaseRebuildService` and implement:

   - ``snapshot_sources`` — property returning ``{service_name: url}``
   - ``clear_tables()`` — delete all rows that will be repopulated
   - ``rebuild_from_snapshots(raw)`` — parse raw JSON and insert rows; return count
   - ``get_status()`` — return a dict with current table row counts

2. Wire up the router in ``main.py``::

       from taca_rebuild import make_rebuild_router
       from .config import Config
       from .database import get_db_session
       from .events import rabbitmq_service
       from .my_rebuild_service import MyRebuildService

       router = make_rebuild_router(
           service_cls=MyRebuildService,
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

__all__ = [
    "BaseRebuildService",
    "make_rebuild_router",
    "RebuildResult",
    "SnapshotFetchError",
    "SnapshotFetcher",
]
