"""
Generic HTTP snapshot fetcher with retry logic.

Services declare which upstream URLs they need; the fetcher handles all the
transport details (timeouts, retries, error translation).
"""

import asyncio
from typing import Dict, Optional

import httpx

from .dto import SnapshotFetchError


class SnapshotFetcher:
    """
    Async HTTP client for fetching raw JSON snapshots from upstream services.

    All retry/timeout logic lives here so concrete rebuild services never have
    to think about network resilience.

    Usage::

        fetcher = SnapshotFetcher(timeout=30, max_retries=3)
        raw = await fetcher.fetch_many({
            "modalities": "http://modalities-service:8000/internal/snapshot",
            "tournaments": "http://tournaments-service:8000/internal/snapshot",
        })
        # raw == {"modalities": {...} or None, "tournaments": {...} or None}
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3) -> None:
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch(self, service_name: str, url: str) -> Optional[dict]:
        """
        Fetch the snapshot from one service endpoint.

        Returns the parsed JSON dict on success, or ``None`` when the service
        responds with 404 (snapshot endpoint not yet implemented).

        Raises :class:`SnapshotFetchError` after exhausting all retries.
        """
        last_exc: Optional[Exception] = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url)

                    if response.status_code == 200:
                        return response.json()

                    if response.status_code == 404:
                        # Endpoint not implemented — treat as empty, not an error.
                        return None

                    last_exc = Exception(
                        f"HTTP {response.status_code}: {response.text[:200]}"
                    )

                except (httpx.TimeoutException, httpx.ConnectError) as exc:
                    last_exc = exc

                except Exception as exc:
                    last_exc = exc

        raise SnapshotFetchError(
            service_name,
            f"Failed after {self.max_retries} attempts",
            last_exc,
        )

    async def fetch_many(self, sources: Dict[str, str]) -> Dict[str, Optional[dict]]:
        """
        Fetch all snapshots concurrently.

        Args:
            sources: Mapping of ``{service_name: snapshot_url}``.

        Returns:
            Mapping of ``{service_name: raw_json_dict_or_None}``.

        Raises:
            :class:`SnapshotFetchError`: If any service fetch fails.
        """
        results = await asyncio.gather(
            *[self.fetch(name, url) for name, url in sources.items()],
            return_exceptions=True,
        )

        output: Dict[str, Optional[dict]] = {}
        for name, result in zip(sources.keys(), results):
            if isinstance(result, Exception):
                raise result
            output[name] = result

        return output
