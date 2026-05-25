"""
FastAPI router factory for SSE-based internal rebuild endpoints.

All microservices expose the same four endpoints under ``/internal``:

- ``POST /internal/rebuild``         — trigger a full SSE-based rebuild
- ``GET  /internal/rebuild/status``  — inspect current table row counts
- ``POST /internal/rebuild/pause``   — manually pause event consumption
- ``POST /internal/rebuild/resume``  — manually resume event consumption

The rebuild endpoint initiates concurrent SSE streams to all snapshot sources,
processing events incrementally. This approach is more efficient for large
datasets compared to single-request fetching.

Every endpoint requires the ``X-INTERNAL-TOKEN`` header and must **not** be
reachable through the public API Gateway.

Usage::

    from taca_rebuild import make_sse_rebuild_router
    from .config import Config
    from .database import get_db_session
    from .events import rabbitmq_service
    from .my_sse_rebuild_service import MySSERebuildService

    router = make_sse_rebuild_router(
        service_cls=MySSERebuildService,
        rabbitmq_svc=rabbitmq_service,
        get_db=get_db_session,
        internal_token=Config.INTERNAL_API_TOKEN,
        # optional:
        timeout=Config.SNAPSHOT_REQUEST_TIMEOUT,
        max_retries=Config.SNAPSHOT_MAX_RETRIES,
    )

    app.include_router(router)
"""

from typing import Any, Callable, Dict, Type

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .sse_service import BaseSSERebuildService


def make_sse_rebuild_router(
    *,
    service_cls: Type[BaseSSERebuildService],
    rabbitmq_svc,
    get_db: Callable,
    after_rebuild: Callable[[Session], int] = None,
    internal_token: str,
    timeout: int = 60,
    max_retries: int = 3,
    prefix: str = "/internal",
) -> APIRouter:
    """
    Build the standard 4-endpoint SSE-based rebuild :class:`APIRouter`.

    Args:
        service_cls:    Your :class:`BaseSSERebuildService` subclass.
        rabbitmq_svc:   The service's RabbitMQ service instance.
        get_db:         FastAPI dependency that yields/returns a DB session.
        internal_token: Expected value of the ``X-INTERNAL-TOKEN`` header.
        timeout:        HTTP timeout (seconds) for SSE connections.
        max_retries:    Retry attempts per SSE endpoint.
        prefix:         URL prefix for all routes (default ``"/internal"``).

    Returns:
        A configured :class:`fastapi.APIRouter`.
    """
    router = APIRouter(prefix=prefix, tags=["internal"])

    def _verify_token(x_internal_token: str = Header(...)) -> bool:
        if x_internal_token != internal_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing internal token",
            )
        return True

    def _make_service(db: Session) -> BaseSSERebuildService:
        return service_cls(
            db_session=db,
            rabbitmq_svc=rabbitmq_svc,
            timeout=timeout,
            max_retries=max_retries,
        )

    def _make_service_no_db() -> BaseSSERebuildService:
        return service_cls(
            db_session=None,
            rabbitmq_svc=rabbitmq_svc,
            timeout=timeout,
            max_retries=max_retries,
        )

    # ------------------------------------------------------------------
    # POST /internal/rebuild — Trigger rebuild
    # ------------------------------------------------------------------

    @router.post("/rebuild", status_code=200, response_model=None)
    async def trigger_rebuild(
        db: Session = Depends(get_db),
        _: bool = Depends(_verify_token),
    ) -> Dict[str, Any]:
        """Trigger a full rebuild via concurrent SSE streams."""
        service = _make_service(db)

        result = await service.execute_rebuild()

        if after_rebuild:
            post_count = await after_rebuild(db)
            result.message += f" | Post-rebuild tasks processed {post_count} records"

        return {
            "success": result.success,
            "message": result.message,
            "records_processed": result.records_processed,
            "duration_seconds": result.duration_seconds,
            "errors": result.errors,
        }

    # ------------------------------------------------------------------
    # GET /internal/rebuild/status — Get status
    # ------------------------------------------------------------------

    @router.get("/rebuild/status", status_code=200, response_model=None)
    async def get_rebuild_status(
        db: Session = Depends(get_db),
        _: bool = Depends(_verify_token),
    ) -> Dict[str, Any]:
        """Inspect current table row counts and rebuild service health."""
        service = _make_service(db)
        status_dict = service.get_status()
        return {"status": status_dict}

    # ------------------------------------------------------------------
    # POST /internal/rebuild/pause — Pause consumption
    # ------------------------------------------------------------------

    @router.post("/rebuild/pause", status_code=200, response_model=None)
    async def pause_consumption(
        _: bool = Depends(_verify_token),
    ) -> Dict[str, Any]:
        """Manually pause event consumption."""
        service = _make_service_no_db()
        await service.pause_event_consumption()
        return {"message": "Event consumption paused"}

    # ------------------------------------------------------------------
    # POST /internal/rebuild/resume — Resume consumption
    # ------------------------------------------------------------------

    @router.post("/rebuild/resume", status_code=200, response_model=None)
    async def resume_consumption(
        _: bool = Depends(_verify_token),
    ) -> Dict[str, Any]:
        """Manually resume event consumption."""
        service = _make_service_no_db()
        await service.resume_event_consumption()
        return {"message": "Event consumption resumed"}

    return router
