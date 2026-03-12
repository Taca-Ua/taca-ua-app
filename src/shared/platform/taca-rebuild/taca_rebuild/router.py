"""
FastAPI router factory for the standard internal rebuild endpoints.

All microservices expose the same four endpoints under ``/internal``:

- ``POST /internal/rebuild``         — trigger a full rebuild
- ``GET  /internal/rebuild/status``  — inspect current table row counts
- ``POST /internal/rebuild/pause``   — manually pause event consumption
- ``POST /internal/rebuild/resume``  — manually resume event consumption

Every endpoint requires the ``X-INTERNAL-TOKEN`` header and must **not** be
reachable through the public API Gateway.

Usage::

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
        # optional:
        timeout=Config.SNAPSHOT_REQUEST_TIMEOUT,
        max_retries=Config.SNAPSHOT_MAX_RETRIES,
    )

    app.include_router(router)
"""

from typing import Callable, Type

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .service import BaseRebuildService


def make_rebuild_router(
    *,
    service_cls: Type[BaseRebuildService],
    rabbitmq_svc,
    get_db: Callable,
    internal_token: str,
    timeout: int = 30,
    max_retries: int = 3,
    prefix: str = "/internal",
) -> APIRouter:
    """
    Build the standard 4-endpoint rebuild :class:`APIRouter`.

    Args:
        service_cls:    Your :class:`BaseRebuildService` subclass.
        rabbitmq_svc:   The service's RabbitMQ service instance.
        get_db:         FastAPI dependency that yields/returns a DB session.
        internal_token: Expected value of the ``X-INTERNAL-TOKEN`` header.
        timeout:        HTTP timeout (seconds) for snapshot requests.
        max_retries:    Retry attempts per snapshot endpoint.
        prefix:         URL prefix for all routes (default ``"/internal"``).

    Returns:
        A configured :class:`fastapi.APIRouter`.
    """
    router = APIRouter(prefix=prefix, tags=["internal"])

    # ------------------------------------------------------------------
    # Auth dependency (captured in closure — not a module-level function
    # so each router instance can have its own token).
    # ------------------------------------------------------------------

    def _verify_token(x_internal_token: str = Header(...)) -> bool:
        if x_internal_token != internal_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing internal token",
            )
        return True

    def _make_service(db: Session) -> BaseRebuildService:
        return service_cls(
            db_session=db,
            rabbitmq_svc=rabbitmq_svc,
            timeout=timeout,
            max_retries=max_retries,
        )

    def _make_service_no_db() -> BaseRebuildService:
        return service_cls(
            db_session=None,
            rabbitmq_svc=rabbitmq_svc,
            timeout=timeout,
            max_retries=max_retries,
        )

    # ------------------------------------------------------------------
    # Endpoints
    # ------------------------------------------------------------------

    @router.post("/rebuild")
    async def trigger_rebuild(
        db: Session = Depends(get_db),
        _: bool = Depends(_verify_token),
    ):
        """
        Trigger a full rebuild of this service's tables.

        **DESTRUCTIVE**: all existing data is wiped and repopulated from
        upstream service snapshots.

        Requires ``X-INTERNAL-TOKEN`` header.
        """
        svc = _make_service(db)
        result = await svc.execute_rebuild()

        if result.success:
            return {
                "success": result.success,
                "message": result.message,
                "records_processed": result.records_processed,
                "duration_seconds": result.duration_seconds,
            }

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": result.success,
                "message": result.message,
                "errors": result.errors,
                "duration_seconds": result.duration_seconds,
            },
        )

    @router.get("/rebuild/status")
    async def rebuild_status(
        db: Session = Depends(get_db),
        _: bool = Depends(_verify_token),
    ):
        """
        Return current row counts for all managed tables.

        Requires ``X-INTERNAL-TOKEN`` header.
        """
        svc = _make_service(db)
        return {"success": True, "status": svc.get_status()}

    @router.post("/rebuild/pause")
    async def pause_event_consumption(
        _: bool = Depends(_verify_token),
    ):
        """
        Manually pause RabbitMQ event consumption.

        Requires ``X-INTERNAL-TOKEN`` header.
        """
        svc = _make_service_no_db()
        await svc.pause_event_consumption()
        return {
            "success": True,
            "message": "Event consumption paused",
            "paused": getattr(rabbitmq_svc, "is_paused", lambda: True)(),
        }

    @router.post("/rebuild/resume")
    async def resume_event_consumption(
        _: bool = Depends(_verify_token),
    ):
        """
        Manually resume RabbitMQ event consumption.

        Requires ``X-INTERNAL-TOKEN`` header.
        """
        svc = _make_service_no_db()
        await svc.resume_event_consumption()
        return {
            "success": True,
            "message": "Event consumption resumed",
            "paused": getattr(rabbitmq_svc, "is_paused", lambda: False)(),
        }

    return router
