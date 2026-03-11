"""
TACA Storage - Shared storage management (MinIO) for all services
"""

from .minio_service import MinioService
from .file_service import FileService

__all__ = ["MinioService", "FileService"]