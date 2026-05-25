"""
Data Transfer Objects for the rebuild framework.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RebuildResult:
    """Result returned by :meth:`BaseRebuildService.execute_rebuild`."""

    success: bool
    message: str
    records_processed: int
    duration_seconds: float
    errors: List[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)


class SnapshotFetchError(Exception):
    """Raised when a snapshot HTTP request fails after all retries."""

    def __init__(
        self,
        service_name: str,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        self.service_name = service_name
        self.original_error = original_error
        super().__init__(f"Failed to fetch snapshot from {service_name}: {message}")
