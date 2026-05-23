"""
Abstract base class for SSE-based microservice rebuild services.

Stream data incrementally from upstream services via Server-Sent Events,
enabling efficient handling of large datasets without loading everything
into memory at once.

Minimal example::

    class MySSERebuildService(BaseSSERebuildService):

        @property
        def snapshot_sources(self):
            return {
                "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot/stream",
                "tournaments": f"{Config.TOURNAMENTS_SERVICE_URL}/internal/snapshot/stream",
            }

        def clear_tables(self):
            self.db.query(MyModel).delete()
            self.db.commit()

        async def rebuild_from_snapshot_event(self, service_name, event):
            # event = {"type": "metadata", "count": ...} or
            #         {"type": "item", "data": {...}} or
            #         {"type": "complete", "records": ...}

            if event["type"] == "item":
                item = event["data"]
                self.db.add(MyModel(id=item["id"], ...))

            elif event["type"] == "complete":
                self.db.commit()
                return event.get("records", 0)

            return 0

        def get_status(self):
            return {"my_table": self.db.query(MyModel).count()}
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Optional

from sqlalchemy.orm import Session

from .dto import RebuildResult
from .sse_fetcher import SSESnapshotFetcher


class BaseSSERebuildService(ABC):
    """
    Template-method base class for streaming rebuild orchestration via SSE.

    Concrete subclasses only need to worry about:
    - *which* URLs provide the SSE streams
    - *how* to process individual events
    - resource cleanup on completion

    Constructor args:
        db_session:   SQLAlchemy Session (may be ``None`` for pause/resume-only use).
        rabbitmq_svc: The service's RabbitMQ service instance.
        timeout:      HTTP timeout in seconds for SSE connections.
        max_retries:  Maximum retry attempts per SSE endpoint.
    """

    def __init__(
        self,
        db_session: Optional[Session],
        rabbitmq_svc,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.db = db_session
        self.rabbitmq_svc = rabbitmq_svc
        self._fetcher = SSESnapshotFetcher(timeout=timeout, max_retries=max_retries)
        self._total_records = 0

    # ------------------------------------------------------------------
    # Abstract interface — the only things a subclass must implement
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def snapshot_sources(self) -> Dict[str, str]:
        """
        Return a mapping of ``{service_name: stream_url}`` to connect to.

        These should be SSE endpoints that emit snapshot events.

        Example::

            return {
                "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot/stream",
                "tournaments": f"{Config.TOURNAMENTS_SERVICE_URL}/internal/snapshot/stream",
            }
        """

    @abstractmethod
    def clear_tables(self) -> None:
        """
        Delete all rows from the tables that will be rebuilt.

        Called after event consumption is paused but before opening SSE streams.
        Must commit (or at minimum flush) before returning.
        """

    @abstractmethod
    async def rebuild_from_snapshot_event(self, service_name: str, event: dict) -> int:
        """
        Process a single snapshot event and return records processed in this event.

        Events have structures like::

            {"type": "metadata", "count": <expected_total>}
            {"type": "item", "data": <object>}
            {"type": "batch", "items": [<obj>, ...]}
            {"type": "complete", "records": <total_count>}

        Args:
            service_name: Name of the service producing this event.
            event:        The SSE event (already parsed JSON).

        Returns:
            Number of records inserted/processed by this event.
            Return 0 for metadata-only events or non-insert events.
        """

    @abstractmethod
    def get_status(self) -> dict:
        """Return a dict describing current table row counts / health."""

    # ------------------------------------------------------------------
    # Pause / Resume
    # ------------------------------------------------------------------

    async def pause_event_consumption(self) -> None:
        if hasattr(self.rabbitmq_svc, "pause_consumption"):
            await self.rabbitmq_svc.pause_consumption()

    async def resume_event_consumption(self) -> None:
        if hasattr(self.rabbitmq_svc, "resume_consumption"):
            await self.rabbitmq_svc.resume_consumption()

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    async def execute_rebuild(self) -> RebuildResult:
        """
        Execute the full streaming rebuild:

        1. Pause event consumption
        2. Clear tables
        3. Open SSE streams to all sources
        4. Process events incrementally via :meth:`rebuild_from_snapshot_event`
        5. Resume event consumption

        Events are processed sequentially from all sources.
        If anything fails, always attempts to resume consumption before returning.
        """
        start = time.time()
        result = RebuildResult(
            success=False,
            message="Rebuild in progress",
            records_processed=0,
            duration_seconds=0.0,
        )
        self._total_records = 0

        try:
            await self.pause_event_consumption()

            self.clear_tables()

            # Process events as they stream in
            for service_name, event in self._fetcher.stream_many(self.snapshot_sources):
                try:
                    records = await self.rebuild_from_snapshot_event(
                        service_name, event
                    )
                    self._total_records += records
                except Exception as exc:
                    result.add_error(
                        f"Error processing {service_name} event: {str(exc)}"
                    )
                    raise

            if self._total_records == 0:
                result.add_error(
                    "No snapshot events received from any upstream service"
                )
                return result

            await self.resume_event_consumption()

            result.success = True
            result.message = "Rebuild completed successfully"
            result.records_processed = self._total_records

        except Exception as exc:
            result.add_error(f"Unexpected error during rebuild: {exc}")
            try:
                await self.resume_event_consumption()
            except Exception:
                pass

        finally:
            result.duration_seconds = time.time() - start

        return result
