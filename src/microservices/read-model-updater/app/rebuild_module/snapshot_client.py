"""
Snapshot HTTP Client for fetching snapshots from domain services.

This client is responsible for:
- Making HTTP requests to domain service snapshot endpoints
- Handling timeouts and retries
- Transforming raw HTTP responses into strongly typed DTOs
- Fail-fast error handling

Architecture Note:
- Services communicate via Docker service name DNS resolution
- No IP addresses are hardcoded
- All URLs come from environment variables (Config class)
"""

from typing import Optional

import httpx
from taca_snapshots.matches import MatchesSnapshotResponse
from taca_snapshots.modalities import ModalitiesSnapshotResponse
from taca_snapshots.tournaments import TournamentsSnapshotResponse

from ..config import Config
from ..logger import logger
from .dto import (
    CompleteSnapshot,
    MatchesSnapshot,
    ModalitiesSnapshot,
    TournamentSnapshot,
)


class SnapshotFetchError(Exception):
    """Custom exception for snapshot fetching errors."""

    def __init__(
        self, service_name: str, message: str, original_error: Exception = None
    ):
        self.service_name = service_name
        self.original_error = original_error
        super().__init__(f"Failed to fetch snapshot from {service_name}: {message}")


class SnapshotClient:
    """
    HTTP client for fetching snapshots from domain microservices.

    This client uses the internal /internal/snapshot endpoint of each service.
    These endpoints are protected and should only be accessible within the
    Docker network (not exposed externally).

    Usage:
        client = SnapshotClient()
        snapshot = await client.fetch_all_snapshots()
    """

    def __init__(self):
        """Initialize snapshot client with configuration."""
        self.timeout = Config.SNAPSHOT_REQUEST_TIMEOUT
        self.max_retries = Config.SNAPSHOT_MAX_RETRIES

    async def _fetch_snapshot(self, service_name: str, url: str) -> Optional[dict]:
        """
        Fetch snapshot from a single service.

        Args:
            service_name: Name of the service (for logging)
            url: Full URL to the snapshot endpoint

        Returns:
            Raw snapshot JSON as a dictionary, or None if service returned 404

        Raises:
            SnapshotFetchError: If fetching fails after retries
        """
        logger.info(
            "snapshot_fetch_started",
            service=service_name,
            url=url,
            timeout=self.timeout,
        )

        # Use httpx for async HTTP requests with timeout
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            retry_count = 0
            last_error = None

            while retry_count < self.max_retries:
                try:
                    response = await client.get(url)

                    # Check if request was successful
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(
                            "snapshot_fetch_success",
                            service=service_name,
                            status_code=response.status_code,
                            retry_count=retry_count,
                        )
                        return data

                    elif response.status_code == 404:
                        # Service doesn't have snapshot endpoint yet
                        logger.warning(
                            "snapshot_endpoint_not_found",
                            service=service_name,
                            status_code=response.status_code,
                        )
                        return None

                    else:
                        # Unexpected status code
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        logger.error(
                            "snapshot_fetch_failed",
                            service=service_name,
                            status_code=response.status_code,
                            error=error_msg,
                        )
                        last_error = Exception(error_msg)

                except httpx.TimeoutException as e:
                    logger.warning(
                        "snapshot_fetch_timeout",
                        service=service_name,
                        retry_count=retry_count,
                        timeout=self.timeout,
                    )
                    last_error = e

                except httpx.ConnectError as e:
                    logger.warning(
                        "snapshot_fetch_connection_error",
                        service=service_name,
                        retry_count=retry_count,
                        error=str(e),
                    )
                    last_error = e

                except Exception as e:
                    logger.error(
                        "snapshot_fetch_unexpected_error",
                        service=service_name,
                        retry_count=retry_count,
                        error=str(e),
                    )
                    last_error = e

                # Increment retry counter
                retry_count += 1

                # Don't retry on 404 - service doesn't support snapshots
                if isinstance(last_error, Exception) and "404" in str(last_error):
                    break

            # All retries exhausted - raise error
            raise SnapshotFetchError(
                service_name=service_name,
                message=f"Failed after {retry_count} retries",
                original_error=last_error,
            )

    async def fetch_matches_snapshot(self) -> Optional[MatchesSnapshot]:
        """
        Fetch snapshot from Matches service.

        Returns:
            MatchesSnapshot with all match-related data (typed DTOs), or None if unavailable
        """
        url = Config.get_snapshot_url("matches")
        if not url:
            logger.warning("snapshot_url_not_configured", service="matches")
            return None

        try:
            data = await self._fetch_snapshot("matches", url)
            if data is None:
                return None

            response = MatchesSnapshotResponse(**data)
            return MatchesSnapshot.from_response(response)
        except SnapshotFetchError:
            # Re-raise to be handled by caller
            raise

    async def fetch_tournament_snapshot(self) -> Optional[TournamentSnapshot]:
        """
        Fetch snapshot from Tournament service.

        Returns:
            TournamentSnapshot with tournament and competitor data (typed DTOs),
            or None if unavailable
        """
        url = Config.get_snapshot_url("tournament")
        if not url:
            logger.warning("snapshot_url_not_configured", service="tournament")
            return None

        try:
            data = await self._fetch_snapshot("tournament", url)
            if data is None:
                return None

            response = TournamentsSnapshotResponse(**data)
            return TournamentSnapshot.from_response(response)
        except SnapshotFetchError:
            raise

    async def fetch_modalities_snapshot(self) -> Optional[ModalitiesSnapshot]:
        """
        Fetch snapshot from Modalities service.

        Returns:
            ModalitiesSnapshot with all modality-related data (typed DTOs),
            or None if unavailable
        """
        url = Config.get_snapshot_url("modalities")
        if not url:
            logger.warning("snapshot_url_not_configured", service="modalities")
            return None

        try:
            data = await self._fetch_snapshot("modalities", url)
            if data is None:
                return None

            response = ModalitiesSnapshotResponse(**data)
            return ModalitiesSnapshot.from_response(response)
        except SnapshotFetchError:
            raise

    async def fetch_all_snapshots(self) -> CompleteSnapshot:
        """
        Fetch snapshots from ALL domain services.

        This method calls all services in parallel and aggregates the results.
        It uses fail-fast approach: if ANY service fails, the entire operation fails.

        Returns:
            CompleteSnapshot containing data from all services

        Raises:
            SnapshotFetchError: If any service fails to provide a snapshot
        """
        logger.info("snapshot_fetch_all_started")

        # Fetch all snapshots (these run sequentially for now, but can be parallelized)
        # Note: We could use asyncio.gather() for parallel fetching if needed
        try:
            matches = await self.fetch_matches_snapshot()
            tournament = await self.fetch_tournament_snapshot()
            modalities = await self.fetch_modalities_snapshot()

            snapshot = CompleteSnapshot(
                matches=matches,
                tournament=tournament,
                modalities=modalities,
            )

            total_records = snapshot.get_total_record_count()
            logger.info(
                "snapshot_fetch_all_success",
                total_records=total_records,
                has_matches=matches is not None,
                has_tournament=tournament is not None,
                has_modalities=modalities is not None,
            )

            return snapshot

        except SnapshotFetchError as e:
            logger.error(
                "snapshot_fetch_all_failed",
                failed_service=e.service_name,
                error=str(e),
            )
            raise
