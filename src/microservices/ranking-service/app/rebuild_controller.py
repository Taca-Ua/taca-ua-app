"""
Rebuild Controller - HTTP endpoints and service for core-table rebuild.

Provides:
- POST /internal/rebuild        — trigger a full core-table rebuild
- GET  /internal/rebuild/status — inspect current table row counts
- POST /internal/rebuild/pause  — manually pause event consumption
- POST /internal/rebuild/resume — manually resume event consumption

Security:
- All endpoints require the X-INTERNAL-TOKEN header.
- These routes must NOT be exposed through the API Gateway.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from taca_snapshots.modalities import (
    CourseSnapshotItem,
    ModalitiesSnapshotResponse,
    ModalitySnapshotItem,
    ModalityTypeSnapshotItem,
)
from taca_snapshots.tournaments import (
    TournamentCompetitorSnapshotItem,
    TournamentRankingPositionSnapshotItem,
    TournamentSnapshotItem,
    TournamentsSnapshotResponse,
)

from .config import Config
from .database import get_db_session
from .events import rabbitmq_service
from .logger import logger
from .models import (
    Course,
    CourseRanking,
    GeneralRanking,
    Modality,
    ModalityRanking,
    ModalityType,
    ModalityTypeEscalao,
    Tournament,
    TournamentCompetitor,
    TournamentResult,
)
from .ranking_processor import compute_all_rankings

router = APIRouter(prefix="/internal", tags=["internal"])


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


def verify_internal_token(x_internal_token: str = Header(...)) -> bool:
    """Reject requests that do not carry the correct internal token."""
    if x_internal_token != Config.INTERNAL_API_TOKEN:
        logger.warning(
            "rebuild_unauthorized_attempt",
            message="Invalid internal token provided",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal token",
        )
    return True


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass
class RebuildResult:
    success: bool
    message: str
    records_processed: int
    duration_seconds: float
    errors: List[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)


@dataclass
class SnapshotData:
    """Aggregated snapshot data from the upstream domain services."""

    modality_types: List[ModalityTypeSnapshotItem]
    modalities: List[ModalitySnapshotItem]
    courses: List[CourseSnapshotItem]
    tournaments: List[TournamentSnapshotItem]
    competitors: List[TournamentCompetitorSnapshotItem]
    ranking_positions: List[TournamentRankingPositionSnapshotItem]

    def has_data(self) -> bool:
        return any(
            [
                self.modality_types,
                self.modalities,
                self.courses,
                self.tournaments,
                self.competitors,
                self.ranking_positions,
            ]
        )

    def total_records(self) -> int:
        return (
            len(self.modality_types)
            + len(self.modalities)
            + len(self.courses)
            + len(self.tournaments)
            + len(self.competitors)
            + len(self.ranking_positions)
        )


# ---------------------------------------------------------------------------
# Rebuild service
# ---------------------------------------------------------------------------


class RankingRebuildService:
    """
    Orchestrates a full rebuild of the ranking-service core tables.

    Steps:
    1. Pause event consumption
    2. Clear all core tables
    3. Fetch snapshots from modalities-service and tournaments-service
    4. Repopulate core tables from snapshot data
    5. Resume event consumption
    """

    def __init__(self, db_session: Session, rabbitmq_svc):
        self.db = db_session
        self.rabbitmq_svc = rabbitmq_svc

    # ------------------------------------------------------------------
    # Public orchestration entry-point
    # ------------------------------------------------------------------

    async def execute_rebuild(self) -> RebuildResult:
        start = time.time()
        result = RebuildResult(
            success=False,
            message="Rebuild in progress",
            records_processed=0,
            duration_seconds=0.0,
        )

        logger.info("rebuild_started", service="ranking")

        try:
            logger.info("rebuild_step", step="pause_event_consumption")
            await self._pause_events()

            logger.info("rebuild_step", step="clear_core_tables")
            self._clear_core_tables()

            logger.info("rebuild_step", step="fetch_snapshots")
            snapshot = await self._fetch_snapshots()

            if not snapshot.has_data():
                result.add_error("No snapshot data returned by upstream services")
                logger.warning("rebuild_no_data")
                return result

            logger.info("rebuild_step", step="rebuild_core_tables")
            records = self._rebuild_core_tables(snapshot)

            logger.info("rebuild_step", step="compute_derived_tables")
            self._compute_derived_tables()

            logger.info("rebuild_step", step="resume_event_consumption")
            await self._resume_events()

            result.success = True
            result.message = "Rebuild completed successfully"
            result.records_processed = records
            result.duration_seconds = time.time() - start

            logger.info(
                "rebuild_completed",
                records_processed=records,
                duration_seconds=result.duration_seconds,
            )

        except Exception as exc:
            result.add_error(f"Unexpected error during rebuild: {exc}")
            logger.error("rebuild_failed", error=str(exc))
            # Always attempt to resume consumption so events are not lost
            try:
                await self._resume_events()
            except Exception as resume_exc:
                logger.error("rebuild_resume_failed_after_error", error=str(resume_exc))

        finally:
            result.duration_seconds = time.time() - start

        return result

    # ------------------------------------------------------------------
    # Pause / resume helpers
    # ------------------------------------------------------------------

    async def _pause_events(self) -> None:
        if hasattr(self.rabbitmq_svc, "pause_consumption"):
            await self.rabbitmq_svc.pause_consumption()
            logger.info("event_consumption_paused")
        else:
            logger.warning(
                "event_consumption_pause_not_implemented",
                message="RabbitMQ service does not support pause; "
                "events may arrive during rebuild.",
            )

    async def _resume_events(self) -> None:
        if hasattr(self.rabbitmq_svc, "resume_consumption"):
            await self.rabbitmq_svc.resume_consumption()
            logger.info("event_consumption_resumed")
        else:
            logger.warning(
                "event_consumption_resume_not_implemented",
                message="RabbitMQ service does not support resume.",
            )

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------

    def _clear_core_tables(self) -> None:
        """
        Delete all rows from the ranking-service core tables.

        Deletion order respects implicit FK dependencies:
        1. TournamentResult   (depends on Tournament)
        2. TournamentCompetitor (depends on Tournament)
        3. Tournament           (depends on Modality)
        4. ModalityTypeEscalao  (depends on ModalityType)
        5. Modality             (depends on ModalityType)
        6. ModalityType
        7. Course               (independent)
        """
        logger.info("core_tables_clearing")
        try:
            self.db.query(TournamentResult).delete()
            self.db.query(TournamentCompetitor).delete()
            self.db.query(Tournament).delete()
            self.db.query(ModalityTypeEscalao).delete()
            self.db.query(Modality).delete()
            self.db.query(ModalityType).delete()
            self.db.query(Course).delete()
            self.db.commit()
            logger.info("core_tables_cleared")
        except Exception as exc:
            self.db.rollback()
            logger.error("core_tables_clear_failed", error=str(exc))
            raise

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------

    async def _fetch_snapshots(self) -> SnapshotData:
        """Fetch required data from modalities-service and tournaments-service."""
        timeout = Config.SNAPSHOT_REQUEST_TIMEOUT
        max_retries = Config.SNAPSHOT_MAX_RETRIES

        modalities_data = await self._get_json(
            "modalities", Config.get_snapshot_url("modalities"), timeout, max_retries
        )
        tournaments_data = await self._get_json(
            "tournaments", Config.get_snapshot_url("tournaments"), timeout, max_retries
        )

        # Parse with strongly typed response models
        mod_resp = (
            ModalitiesSnapshotResponse(**modalities_data) if modalities_data else None
        )
        tour_resp = (
            TournamentsSnapshotResponse(**tournaments_data)
            if tournaments_data
            else None
        )

        return SnapshotData(
            modality_types=mod_resp.modality_types if mod_resp else [],
            modalities=mod_resp.modalities if mod_resp else [],
            courses=mod_resp.courses if mod_resp else [],
            tournaments=tour_resp.tournaments if tour_resp else [],
            competitors=tour_resp.competitors if tour_resp else [],
            ranking_positions=tour_resp.ranking_positions if tour_resp else [],
        )

    async def _get_json(
        self, service_name: str, url: Optional[str], timeout: int, max_retries: int
    ) -> Optional[dict]:
        if not url:
            logger.warning("snapshot_url_not_configured", service=service_name)
            return None

        logger.info("snapshot_fetch_started", service=service_name, url=url)
        last_exc: Optional[Exception] = None

        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        logger.info(
                            "snapshot_fetch_success",
                            service=service_name,
                            attempt=attempt,
                        )
                        return response.json()
                    if response.status_code == 404:
                        logger.warning(
                            "snapshot_endpoint_not_found",
                            service=service_name,
                        )
                        return None
                    last_exc = Exception(
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    logger.error(
                        "snapshot_fetch_failed",
                        service=service_name,
                        status_code=response.status_code,
                    )
                except (httpx.TimeoutException, httpx.ConnectError) as exc:
                    last_exc = exc
                    logger.warning(
                        "snapshot_fetch_network_error",
                        service=service_name,
                        attempt=attempt,
                        error=str(exc),
                    )
                except Exception as exc:
                    last_exc = exc
                    logger.error(
                        "snapshot_fetch_unexpected_error",
                        service=service_name,
                        attempt=attempt,
                        error=str(exc),
                    )

        raise RuntimeError(
            f"Failed to fetch snapshot from {service_name} "
            f"after {max_retries} attempts: {last_exc}"
        )

    # ------------------------------------------------------------------
    # Rebuild
    # ------------------------------------------------------------------

    def _rebuild_core_tables(self, snapshot: SnapshotData) -> int:
        """
        Insert all snapshot data in dependency order:
        1. ModalityType
        2. ModalityTypeEscalao  (after ModalityType)
        3. Modality             (after ModalityType)
        4. Course
        5. Tournament           (after Modality)
        6. TournamentCompetitor (after Tournament)
        7. TournamentResult     (after Tournament)
        """
        try:
            total = 0
            total += self._insert_modality_types(snapshot.modality_types)
            total += self._insert_modalities(snapshot.modalities)
            total += self._insert_courses(snapshot.courses)
            total += self._insert_tournaments(snapshot.tournaments)
            total += self._insert_competitors(snapshot.competitors)
            total += self._insert_ranking_positions(snapshot.ranking_positions)
            self.db.commit()
            logger.info("core_tables_rebuilt", total_records=total)
            return total
        except Exception as exc:
            self.db.rollback()
            logger.error("core_tables_rebuild_failed", error=str(exc))
            raise

    def _insert_modality_types(self, items: List[ModalityTypeSnapshotItem]) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(ModalityType(modality_type_id=item.id))
            for escalao in item.escaloes or []:
                self.db.add(
                    ModalityTypeEscalao(
                        modality_type_id=item.id,
                        min_participants=escalao.min_participants,
                        max_participants=escalao.max_participants,
                        points=escalao.points,
                    )
                )
        self.db.flush()
        # Count both ModalityType rows and their escalao rows
        escalao_count = sum(len(item.escaloes or []) for item in items)
        logger.debug(
            "core_table_rebuilt",
            table="modality_types",
            count=len(items),
            escalao_count=escalao_count,
        )
        return len(items) + escalao_count

    def _insert_modalities(self, items: List[ModalitySnapshotItem]) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                Modality(
                    modality_id=item.id,
                    modality_type_id=item.modality_type_id,
                )
            )
        self.db.flush()
        logger.debug("core_table_rebuilt", table="modalities", count=len(items))
        return len(items)

    def _insert_courses(self, items: List[CourseSnapshotItem]) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(Course(course_id=item.id))
        self.db.flush()
        logger.debug("core_table_rebuilt", table="courses", count=len(items))
        return len(items)

    def _insert_tournaments(self, items: List[TournamentSnapshotItem]) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                Tournament(
                    tournament_id=item.id,
                    modality_id=item.modality_id,
                    scoring_format_id=item.scoring_format_id,
                )
            )
        self.db.flush()
        logger.debug("core_table_rebuilt", table="tournaments", count=len(items))
        return len(items)

    def _insert_competitors(self, items: List[TournamentCompetitorSnapshotItem]) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                TournamentCompetitor(
                    tournament_id=item.tournament_id,
                    competitor_id=item.id,
                )
            )
        self.db.flush()
        logger.debug(
            "core_table_rebuilt", table="tournament_competitors", count=len(items)
        )
        return len(items)

    # ------------------------------------------------------------------
    # Derived tables
    # ------------------------------------------------------------------

    def _compute_derived_tables(self) -> None:
        """Recompute all derived ranking tables from the freshly rebuilt core tables."""
        try:
            compute_all_rankings(self.db)
            self.db.commit()
            logger.info("derived_tables_computed")
        except Exception as exc:
            self.db.rollback()
            logger.error("derived_tables_compute_failed", error=str(exc))
            raise

    def _insert_ranking_positions(
        self, items: List[TournamentRankingPositionSnapshotItem]
    ) -> int:
        if not items:
            return 0
        for item in items:
            self.db.add(
                TournamentResult(
                    tournament_id=item.tournament_id,
                    competitor_id=item.competitor_id,
                    position=item.position,
                )
            )
        self.db.flush()
        logger.debug("core_table_rebuilt", table="tournament_results", count=len(items))
        return len(items)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        try:
            return {
                "core_tables": {
                    "modality_types": self.db.query(ModalityType).count(),
                    "modality_type_escaloes": self.db.query(
                        ModalityTypeEscalao
                    ).count(),
                    "modalities": self.db.query(Modality).count(),
                    "courses": self.db.query(Course).count(),
                    "tournaments": self.db.query(Tournament).count(),
                    "tournament_competitors": self.db.query(
                        TournamentCompetitor
                    ).count(),
                    "tournament_results": self.db.query(TournamentResult).count(),
                },
                "derived_tables": {
                    "modality_rankings": self.db.query(ModalityRanking).count(),
                    "course_rankings": self.db.query(CourseRanking).count(),
                    "general_rankings": self.db.query(GeneralRanking).count(),
                },
                "event_consumption_paused": getattr(
                    self.rabbitmq_svc, "is_paused", lambda: False
                )(),
            }
        except Exception as exc:
            logger.error("rebuild_status_check_failed", error=str(exc))
            return {"error": "Failed to retrieve status", "message": str(exc)}


# ---------------------------------------------------------------------------
# HTTP endpoints
# ---------------------------------------------------------------------------


@router.post("/rebuild")
async def trigger_rebuild(
    db: Session = Depends(get_db_session),
    _: bool = Depends(verify_internal_token),
):
    """
    Trigger a full rebuild of the ranking-service core tables.

    **DESTRUCTIVE**: all existing core-table data is wiped and repopulated
    from upstream service snapshots.

    Requires X-INTERNAL-TOKEN header.
    """
    logger.info(
        "rebuild_triggered",
        message="Rebuild request received via HTTP endpoint",
    )

    try:
        svc = RankingRebuildService(db_session=db, rabbitmq_svc=rabbitmq_service)
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

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("rebuild_endpoint_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rebuild failed with unexpected error: {exc}",
        )


@router.get("/rebuild/status")
async def get_rebuild_status(
    db: Session = Depends(get_db_session),
    _: bool = Depends(verify_internal_token),
):
    """
    Return current row counts for all ranking-service core tables.

    Requires X-INTERNAL-TOKEN header.
    """
    logger.info("rebuild_status_requested")
    try:
        svc = RankingRebuildService(db_session=db, rabbitmq_svc=rabbitmq_service)
        return {"success": True, "status": svc.get_status()}
    except Exception as exc:
        logger.error("rebuild_status_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {exc}",
        )


@router.post("/rebuild/pause")
async def pause_event_consumption(
    _: bool = Depends(verify_internal_token),
):
    """
    Manually pause RabbitMQ event consumption.

    Requires X-INTERNAL-TOKEN header.
    """
    logger.info("event_consumption_pause_requested")
    try:
        svc = RankingRebuildService(db_session=None, rabbitmq_svc=rabbitmq_service)
        await svc._pause_events()
        return {
            "success": True,
            "message": "Event consumption paused",
            "paused": getattr(rabbitmq_service, "is_paused", lambda: True)(),
        }
    except Exception as exc:
        logger.error("event_consumption_pause_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause event consumption: {exc}",
        )


@router.post("/rebuild/resume")
async def resume_event_consumption(
    _: bool = Depends(verify_internal_token),
):
    """
    Manually resume RabbitMQ event consumption.

    Requires X-INTERNAL-TOKEN header.
    """
    logger.info("event_consumption_resume_requested")
    try:
        svc = RankingRebuildService(db_session=None, rabbitmq_svc=rabbitmq_service)
        await svc._resume_events()
        return {
            "success": True,
            "message": "Event consumption resumed",
            "paused": getattr(rabbitmq_service, "is_paused", lambda: False)(),
        }
    except Exception as exc:
        logger.error("event_consumption_resume_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume event consumption: {exc}",
        )
