"""
Read-model-updater rebuild controller.

Wires the standard internal rebuild router to :class:`ReadModelRebuildService`
using :func:`make_rebuild_router` from the shared ``taca-rebuild`` package.

Exposed endpoints (all require ``X-INTERNAL-TOKEN``):
- POST /internal/rebuild
- GET  /internal/rebuild/status
- POST /internal/rebuild/pause
- POST /internal/rebuild/resume
"""

from taca_rebuild import make_rebuild_router

from .config import Config
from .database import get_db_session
from .events import rabbitmq_service
from .rebuild_module.rebuild_service import ReadModelRebuildService

router = make_rebuild_router(
    service_cls=ReadModelRebuildService,
    rabbitmq_svc=rabbitmq_service,
    get_db=get_db_session,
    internal_token=Config.INTERNAL_API_TOKEN,
    timeout=Config.SNAPSHOT_REQUEST_TIMEOUT,
    max_retries=Config.SNAPSHOT_MAX_RETRIES,
)
