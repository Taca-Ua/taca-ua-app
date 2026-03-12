"""
Abstract base class for microservice rebuild services.

Subclass :class:`BaseRebuildService` and implement four methods to get a
fully-featured rebuild service with pause/resume, HTTP snapshot fetching,
retry logic and structured logging out of the box.

Minimal example::

    class MyRebuildService(BaseRebuildService):

        @property
        def snapshot_sources(self):
            return {
                "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot",
                "tournaments": f"{Config.TOURNAMENTS_SERVICE_URL}/internal/snapshot",
            }

        def clear_tables(self):
            self.db.query(MyModel).delete()
            self.db.commit()

        def rebuild_from_snapshots(self, raw):
            # raw["modalities"] / raw["tournaments"] are plain dicts (or None)
            if raw["modalities"]:
                data = ModalitiesSnapshotResponse(**raw["modalities"])
                for item in data.modalities:
                    self.db.add(MyModel(id=item.id, ...))
            self.db.commit()
            return total_count

        def get_status(self):
            return {"my_table": self.db.query(MyModel).count()}
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Optional

from sqlalchemy.orm import Session

from .dto import RebuildResult
from .fetcher import SnapshotFetcher


class BaseRebuildService(ABC):
    """
    Template-method base class for microservice rebuild orchestration.

    Concrete subclasses only need to worry about *what* data to fetch and
    *how* to store it — all transport, retry, pause/resume and error handling
    is provided here.

    Constructor args:
        db_session:   SQLAlchemy Session (may be ``None`` for pause/resume-only use).
        rabbitmq_svc: The service's RabbitMQ service instance.
        timeout:      HTTP timeout in seconds for snapshot requests.
        max_retries:  Maximum HTTP retry attempts per snapshot endpoint.
    """

    def __init__(
        self,
        db_session: Optional[Session],
        rabbitmq_svc,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        self.db = db_session
        self.rabbitmq_svc = rabbitmq_svc
        self._fetcher = SnapshotFetcher(timeout=timeout, max_retries=max_retries)

    # ------------------------------------------------------------------
    # Abstract interface — the only things a subclass must implement
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def snapshot_sources(self) -> Dict[str, str]:
        """
        Return a mapping of ``{service_name: snapshot_url}`` to fetch.

        Example::

            return {
                "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot",
                "tournaments": f"{Config.TOURNAMENTS_SERVICE_URL}/internal/snapshot",
            }
        """

    @abstractmethod
    def clear_tables(self) -> None:
        """
        Delete all rows from the tables that will be rebuilt.

        Called after event consumption is paused but before fetching snapshots.
        Must commit (or at minimum flush) before returning.
        """

    @abstractmethod
    def rebuild_from_snapshots(self, raw: Dict[str, Optional[dict]]) -> int:
        """
        Populate tables from raw snapshot data and return the record count.

        Args:
            raw: Mapping of ``{service_name: json_dict_or_None}`` whose keys
                 match :attr:`snapshot_sources`.  A ``None`` value means the
                 upstream endpoint returned 404 (not yet implemented).

        Returns:
            Total number of rows inserted.
        """

    @abstractmethod
    def get_status(self) -> dict:
        """Return a dict describing current table row counts / health."""

    # ------------------------------------------------------------------
    # Pause / Resume  (duck-typed — works with any RabbitMQ service impl)
    # ------------------------------------------------------------------

    async def pause_event_consumption(self) -> None:
        if hasattr(self.rabbitmq_svc, "pause_consumption"):
            await self.rabbitmq_svc.pause_consumption()

    async def resume_event_consumption(self) -> None:
        if hasattr(self.rabbitmq_svc, "resume_consumption"):
            await self.rabbitmq_svc.resume_consumption()

    # ------------------------------------------------------------------
    # Orchestration — do not override unless you have a very good reason
    # ------------------------------------------------------------------

    async def execute_rebuild(self) -> RebuildResult:
        """
        Execute the full rebuild:

        1. Pause event consumption
        2. Clear tables  (``clear_tables``)
        3. Fetch snapshots  (``snapshot_sources`` + :class:`SnapshotFetcher`)
        4. Rebuild tables  (``rebuild_from_snapshots``)
        5. Resume event consumption

        If anything fails the service always attempts to resume consumption
        before propagating the error result.
        """
        start = time.time()
        result = RebuildResult(
            success=False,
            message="Rebuild in progress",
            records_processed=0,
            duration_seconds=0.0,
        )

        try:
            await self.pause_event_consumption()

            self.clear_tables()

            raw = await self._fetcher.fetch_many(self.snapshot_sources)

            if not any(v is not None for v in raw.values()):
                result.add_error("No snapshot data returned by any upstream service")
                return result

            records = self.rebuild_from_snapshots(raw)

            await self.resume_event_consumption()

            result.success = True
            result.message = "Rebuild completed successfully"
            result.records_processed = records

        except Exception as exc:
            result.add_error(f"Unexpected error during rebuild: {exc}")
            try:
                await self.resume_event_consumption()
            except Exception:
                pass

        finally:
            result.duration_seconds = time.time() - start

        return result
