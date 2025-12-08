"""
MinIO Storage Service for file uploads with unique hash
"""

import hashlib
import os
from datetime import timedelta
from typing import Optional

from minio import Minio
from minio.error import S3Error


class MinIOStorageService:
    """Service to handle file uploads to MinIO with unique hash-based filenames"""

    def __init__(
        self,
        endpoint: str = "minio:9000",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: bool = False,
    ):
        """
        Initialize MinIO client

        Args:
            endpoint: MinIO server endpoint
            access_key: MinIO access key (defaults to env MINIO_ROOT_USER)
            secret_key: MinIO secret key (defaults to env MINIO_ROOT_PASSWORD)
            secure: Use HTTPS (default False for local dev)
        """
        self.client = Minio(
            endpoint,
            access_key=access_key or os.getenv("MINIO_ROOT_USER", "admin"),
            secret_key=secret_key or os.getenv("MINIO_ROOT_PASSWORD", "adminadmin"),
            secure=secure,
        )
        self.regulations_bucket = "regulations"
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.regulations_bucket):
                self.client.make_bucket(self.regulations_bucket)
                print(f"Bucket '{self.regulations_bucket}' created successfully")
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise

    def _generate_file_hash(self, file_content: bytes) -> str:
        """
        Generate SHA256 hash of file content

        Args:
            file_content: File content in bytes

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(file_content).hexdigest()

    def upload_file(
        self,
        file_content: bytes,
        original_filename: str,
        content_type: str = "application/pdf",
    ) -> dict:
        """
        Upload file to MinIO with hash-based unique filename

        Args:
            file_content: File content in bytes
            original_filename: Original filename (used for extension)
            content_type: MIME type of the file

        Returns:
            Dictionary with file info including hash, url, and size
        """
        try:
            # Generate unique hash
            file_hash = self._generate_file_hash(file_content)

            # Get file extension
            _, ext = os.path.splitext(original_filename)
            if not ext:
                ext = ".pdf"  # Default to PDF for regulations

            # Create unique filename: hash + extension
            unique_filename = f"{file_hash}{ext}"

            # Check if file already exists (same hash = same content)
            try:
                stat = self.client.stat_object(self.regulations_bucket, unique_filename)
                return {
                    "hash": file_hash,
                    "filename": unique_filename,
                    "url": self._get_file_url(unique_filename),
                    "size": stat.size,
                    "already_exists": True,
                }
            except S3Error:
                # File doesn't exist, proceed with upload
                pass

            # Upload file
            from io import BytesIO

            file_stream = BytesIO(file_content)
            file_size = len(file_content)

            self.client.put_object(
                self.regulations_bucket,
                unique_filename,
                file_stream,
                file_size,
                content_type=content_type,
            )

            return {
                "hash": file_hash,
                "filename": unique_filename,
                "url": self._get_file_url(unique_filename),
                "size": file_size,
                "already_exists": False,
            }

        except S3Error as e:
            print(f"Error uploading file: {e}")
            raise

    def _get_file_url(self, filename: str) -> str:
        """
        Get public URL for a file

        Args:
            filename: Name of the file in MinIO

        Returns:
            Public URL string
        """
        # For production, you might want to use presigned URLs
        # For now, return the direct URL
        return f"http://localhost:9000/{self.regulations_bucket}/{filename}"

    def get_presigned_url(
        self, filename: str, expiry: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Get presigned URL for temporary access

        Args:
            filename: Name of the file in MinIO
            expiry: URL expiration time

        Returns:
            Presigned URL string
        """
        try:
            url = self.client.presigned_get_object(
                self.regulations_bucket, filename, expires=expiry
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            raise

    def delete_file(self, filename: str) -> bool:
        """
        Delete file from MinIO

        Args:
            filename: Name of the file to delete

        Returns:
            True if successful
        """
        try:
            self.client.remove_object(self.regulations_bucket, filename)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False

    def file_exists(self, file_hash: str, extension: str = ".pdf") -> bool:
        """
        Check if file with given hash exists

        Args:
            file_hash: SHA256 hash of the file
            extension: File extension

        Returns:
            True if file exists
        """
        try:
            filename = f"{file_hash}{extension}"
            self.client.stat_object(self.regulations_bucket, filename)
            return True
        except S3Error:
            return False
