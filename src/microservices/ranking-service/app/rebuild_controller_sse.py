"""
Ranking SSE rebuild controller.

SSE-based version of the rebuild service that streams snapshot data
from upstream services instead of fetching entire snapshots at once.

Exposes the standard internal rebuild endpoints (all require ``X-INTERNAL-TOKEN``):
- POST /internal/rebuild
- GET  /internal/rebuild/status
- POST /internal/rebuild/pause
- POST /internal/rebuild/resume
"""

from typing import Dict, List

from sqlalchemy.orm import Session
from taca_rebuild import BaseSSERebuildService, make_sse_rebuild_router
from taca_snapshots import modalities as modality_snapshots
from taca_snapshots import tournaments as tournament_snapshots

from .config import Config
from .database import get_db_session
from .events import rabbitmq_service
from .logger import logger
from .models import (
    Course,
    Modality,
    ModalityType,
    ModalityTypeEscalao,
    Tournament,
    TournamentCompetitor,
    TournamentResult,
)
from .outbox_publisher import outbox_publisher
from .ranking_processor import compute_all_rankings, emit_ranking_computed_event


class ReadModelSSERebuildService(BaseSSERebuildService):
    """
    SSE-based rebuild service for the Read Model Updater.

    Streams snapshots from upstream services via Server-Sent Events,
    processing events incrementally as they arrive. This is more memory-
    efficient than the HTTP approach for large datasets.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track which services we've received complete events from
        self._service_complete = {}

    @property
    def snapshot_sources(self) -> Dict[str, str]:
        return {
            "modalities": f"{Config.MODALITIES_SERVICE_URL}/internal/snapshot/stream",
            "tournaments": f"{Config.TOURNAMENTS_SERVICE_URL}/internal/snapshot/stream",
        }

    def clear_tables(self) -> None:
        logger.info("projections_clearing")
        self.db.query(TournamentCompetitor).delete()
        self.db.query(TournamentResult).delete()
        self.db.query(Tournament).delete()
        self.db.query(Modality).delete()
        self.db.query(ModalityType).delete()
        self.db.query(Course).delete()
        self.db.query(ModalityTypeEscalao).delete()
        self.db.flush()
        logger.info("projections_cleared")

    async def rebuild_from_snapshot_event(self, service_name: str, event: dict) -> int:
        """
        Process snapshot events incrementally as they arrive.

        Event types:
        - metadata: Informational, just log
        - batch: Process items and flush
        - complete: Final commit for this service
        - error: Log and skip
        """
        event_type = event.get("type", "")

        if event_type == "metadata":
            count = event.get("count", 0)
            logger.info(f"{service_name}_snapshot_metadata", count=count)
            return 0

        if event_type == "batch":
            items = event.get("items", [])
            category = event.get("category", "unknown")
            return await self._process_batch(service_name, category, items)

        if event_type == "complete":
            count = event.get("records", 0)
            self._service_complete[service_name] = True
            self.db.commit()
            logger.info(f"{service_name}_snapshot_complete", records=count)
            return 0

        if event_type == "error":
            message = event.get("message", "Unknown error")
            logger.error(f"{service_name}_snapshot_error", message=message)
            return 0

        return 0

    async def _process_batch(
        self, service_name: str, category: str, items: List[dict]
    ) -> int:
        """Process a batch of items based on service and category."""
        if not items:
            return 0

        records = 0

        if service_name == "modalities":
            records = self._process_modalities_batch(category, items)

        elif service_name == "tournaments":
            records = self._process_tournaments_batch(category, items)

        if records > 0:
            self.db.flush()

        return records

    def _process_modalities_batch(self, category: str, items: List[dict]) -> int:
        """Process modalities service batch events."""
        count = 0

        if category == "courses":
            self.db.bulk_save_objects(
                [
                    Course(course_id=item.id)
                    for item in map(
                        lambda x: modality_snapshots.CourseSnapshotItem(**x), items
                    )
                ]
            )
            count += len(items)

        elif category == "modality_types":
            transformed_items = [
                modality_snapshots.ModalityTypeSnapshotItem(**x) for x in items
            ]
            self.db.bulk_save_objects(
                [
                    ModalityType(
                        season_id=item.season_id,
                        modality_type_id=item.id,
                    )
                    for item in transformed_items
                ]
            )
            count += len(items)

            self.db.bulk_save_objects(
                [
                    ModalityTypeEscalao(
                        modality_type_id=item.id,
                        name=escalao.name,
                        min_participants=escalao.min_participants,
                        max_participants=escalao.max_participants,
                        points=escalao.points,
                    )
                    for item in transformed_items
                    for escalao in item.escaloes
                ]
            )
            count += len(items)

        elif category == "modalities":
            self.db.bulk_save_objects(
                [
                    Modality(
                        modality_id=item.id,
                        modality_type_id=item.modality_type_id,
                    )
                    for item in map(
                        lambda x: modality_snapshots.ModalitySnapshotItem(**x), items
                    )
                ]
            )
            count += len(items)

        return count

    def _process_tournaments_batch(self, category: str, items: List[dict]) -> int:
        """Process tournaments service batch events."""
        count = 0

        if category == "tournaments":
            self.db.bulk_save_objects(
                [
                    Tournament(
                        tournament_id=item.id,
                        modality_id=item.modality_id,
                        scoring_format_id=item.scoring_format_id,
                        season_id=item.season_id,
                    )
                    for item in map(
                        lambda x: tournament_snapshots.TournamentSnapshotItem(**x),
                        items,
                    )
                ]
            )
            count += len(items)

        elif category == "competitors":
            self.db.bulk_save_objects(
                [
                    TournamentCompetitor(
                        tournament_id=item.tournament_id,
                        competitor_id=item.id,
                        competitor_course_id=item.competitor_course_id,
                    )
                    for item in map(
                        lambda x: tournament_snapshots.TournamentCompetitorSnapshotItem(
                            **x
                        ),
                        items,
                    )
                ]
            )
            count += len(items)

        elif category == "ranking_positions":
            self.db.bulk_save_objects(
                [
                    TournamentResult(
                        tournament_id=item.tournament_id,
                        competitor_id=item.competitor_id,
                        position=item.position,
                    )
                    for item in map(
                        lambda x: tournament_snapshots.TournamentRankingPositionSnapshotItem(
                            **x
                        ),
                        items,
                    )
                ]
            )
            count += len(items)

        return count

    def get_status(self) -> dict:
        try:
            return {
                "core_projections": {
                    "tournaments": self.db.query(Tournament).count(),
                    "modalities": self.db.query(Modality).count(),
                },
                "event_consumption_paused": getattr(
                    self.rabbitmq_svc, "is_paused", lambda: False
                )(),
            }
        except Exception as exc:
            logger.error("rebuild_status_check_failed", error=str(exc))
            return {"error": "Failed to retrieve status", "message": str(exc)}


async def post_rebuild_tasks(db: Session) -> int:
    """Example post-rebuild task: compute rankings after rebuild."""
    count = 0
    print("Starting post-rebuild tasks: computing rankings...", flush=True)
    try:
        seasons = db.query(Tournament.season_id).distinct().all()
        for (season_id,) in seasons:
            count += compute_all_rankings(db, season_id)
            emit_ranking_computed_event(db, outbox_publisher, season_id)
        db.commit()
        return count  # Return the count of processed records
    except Exception as exc:
        logger.error("post_rebuild_tasks_failed", error=str(exc))
        return 0


router = make_sse_rebuild_router(
    service_cls=ReadModelSSERebuildService,
    rabbitmq_svc=rabbitmq_service,
    get_db=get_db_session,
    after_rebuild=post_rebuild_tasks,
    internal_token=Config.INTERNAL_API_TOKEN,
    timeout=Config.SNAPSHOT_REQUEST_TIMEOUT,
    max_retries=Config.SNAPSHOT_MAX_RETRIES,
)
