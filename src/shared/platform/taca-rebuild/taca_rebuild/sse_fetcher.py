"""
Server-Sent Events (SSE) snapshot fetcher for streaming large datasets.

Instead of loading entire snapshots into memory, SSE streams data as events,
enabling incremental processing and better resource utilization for large
datasets.
"""

import json
import time
from typing import Iterator, Optional

import httpx

from .dto import SnapshotFetchError


class SSESnapshotFetcher:
    """
    SSE client for streaming raw JSON snapshot events from upstream services.

    Designed for large datasets that would be inefficient to load entirely into memory.
    Processes events incrementally as they arrive.

    Usage::

        fetcher = SSESnapshotFetcher(timeout=60, max_retries=3)

        for event in fetcher.stream_events("modalities", sse_url):
            # event = {"type": "item", "data": {...}} or
            #         {"type": "metadata", "count": 1000} or
            #         {"type": "complete"}
            process(event)
    """

    def __init__(self, timeout: int = 60, max_retries: int = 3) -> None:
        self.timeout = timeout
        self.max_retries = max_retries

    def stream_events(self, service_name: str, url: str) -> Iterator[dict]:
        """
        Stream snapshot events from an SSE endpoint.

        Yields events with structure:
        - ``{"type": "metadata", "count": <total_items>}`` — initial metadata
        - ``{"type": "item", "data": <json_object>}`` — individual items
        - ``{"type": "complete", "records": <count>}`` — stream complete

        Args:
            service_name: Name of the upstream service (for error messages).
            url: SSE endpoint URL.

        Raises:
            SnapshotFetchError: After exhausting all retries or on protocol errors.
        """
        last_exc: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    with client.stream("GET", url) as response:
                        if response.status_code == 404:
                            # Endpoint not implemented — emit empty complete
                            yield {"type": "complete", "records": 0}
                            return

                        if response.status_code != 200:
                            last_exc = Exception(
                                f"HTTP {response.status_code}: "
                                f"{response.text[:200] if hasattr(response, 'text') else 'unknown'}"
                            )
                            continue

                        # Process SSE stream
                        for line in response.iter_lines():
                            if not line:
                                continue

                            if line.startswith("data:"):
                                try:
                                    data_str = line[5:].strip()
                                    event = json.loads(data_str)
                                    yield event
                                except json.JSONDecodeError as e:
                                    last_exc = e
                                    raise

                        # Successfully completed streaming
                        return

            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    time.sleep(0.5 * (2**attempt))  # exponential backoff
                    continue

            except Exception as exc:
                last_exc = exc
                raise

        raise SnapshotFetchError(
            service_name,
            f"Failed after {self.max_retries} attempts",
            last_exc,
        )

    def stream_many(self, sources: dict[str, str]) -> Iterator[tuple[str, dict]]:
        """
        Stream events from multiple services sequentially.

        Args:
            sources: Mapping of ``{service_name: sse_url}``.

        Yields:
            Tuples of ``(service_name, event)`` in the order they arrive.

        Raises:
            SnapshotFetchError: If any service stream fails.
        """
        for service_name, url in sources.items():
            for event in self.stream_events(service_name, url):
                yield (service_name, event)
