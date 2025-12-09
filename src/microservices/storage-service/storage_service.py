"""
Generic MinIO Storage Service
Microservice for file storage with hash-based deduplication
"""

import hashlib
import os
from datetime import timedelta
from io import BytesIO
from typing import Dict, Optional

from minio import Minio
from minio.error import S3Error


class StorageService:
    """Generic storage service for file uploads with hash-based deduplication"""

    def __init__(
        self,
        endpoint: str = "minio:9000",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: bool = False,
        default_bucket: str = "files",
    ):
        """
        Initialize MinIO client

        Args:
            endpoint: MinIO server endpoint
            access_key: MinIO access key
            secret_key: MinIO secret key
            secure: Use HTTPS
            default_bucket: Default bucket name
        """
        self.client = Minio(
            endpoint,
            access_key=access_key or os.getenv("MINIO_ROOT_USER", "admin"),
            secret_key=secret_key or os.getenv("MINIO_ROOT_PASSWORD", "adminadmin"),
            secure=secure,
        )
        self.default_bucket = default_bucket
        self._ensure_bucket_exists(self.default_bucket)

    def _ensure_bucket_exists(self, bucket_name: str):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created successfully")

                # Set public read policy for development
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                        }
                    ],
                }
                import json

                self.client.set_bucket_policy(bucket_name, json.dumps(policy))
                print(f"Bucket '{bucket_name}' set to public read access")
        except S3Error as e:
            print(f"Error creating bucket: {e}")
            raise

    def _generate_file_hash(self, file_content: bytes) -> str:
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

    def upload_file(
        self,
        file_content: bytes,
        original_filename: str,
        content_type: str = "application/octet-stream",
        bucket: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        Upload file to MinIO with hash-based unique filename

        Args:
            file_content: File content in bytes
            original_filename: Original filename (used for extension)
            content_type: MIME type of the file
            bucket: Bucket name (uses default if not specified)
            metadata: Additional metadata to store with file

        Returns:
            Dictionary with file info including hash, url, and size
        """
        bucket_name = bucket or self.default_bucket
        self._ensure_bucket_exists(bucket_name)

        try:
            # Generate unique hash
            file_hash = self._generate_file_hash(file_content)

            # Get file extension
            _, ext = os.path.splitext(original_filename)
            if not ext:
                ext = ""

            # Create unique filename: hash + extension
            unique_filename = f"{file_hash}{ext}"

            # Check if file already exists
            try:
                stat = self.client.stat_object(bucket_name, unique_filename)
                return {
                    "success": True,
                    "hash": file_hash,
                    "filename": unique_filename,
                    "original_filename": original_filename,
                    "url": self._get_file_url(unique_filename, bucket_name),
                    "size": stat.size,
                    "content_type": content_type,
                    "bucket": bucket_name,
                    "already_exists": True,
                }
            except S3Error:
                # File doesn't exist, proceed with upload
                pass

            # Prepare metadata
            file_metadata = metadata or {}
            file_metadata["original_filename"] = original_filename

            # Upload file
            file_stream = BytesIO(file_content)
            file_size = len(file_content)

            self.client.put_object(
                bucket_name,
                unique_filename,
                file_stream,
                file_size,
                content_type=content_type,
                metadata=file_metadata,
            )

            return {
                "success": True,
                "hash": file_hash,
                "filename": unique_filename,
                "original_filename": original_filename,
                "url": self._get_file_url(unique_filename, bucket_name),
                "size": file_size,
                "content_type": content_type,
                "bucket": bucket_name,
                "already_exists": False,
            }

        except S3Error as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _get_file_url(self, filename: str, bucket: str) -> str:
        """Get public URL for a file"""
        endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "localhost:9000")
        protocol = (
            "https" if os.getenv("MINIO_SECURE", "false").lower() == "true" else "http"
        )
        return f"{protocol}://{endpoint}/{bucket}/{filename}"

    def get_presigned_url(
        self,
        filename: str,
        bucket: Optional[str] = None,
        expiry: timedelta = timedelta(hours=1),
    ) -> Optional[str]:
        """Get presigned URL for temporary access"""
        bucket_name = bucket or self.default_bucket
        try:
            url = self.client.presigned_get_object(
                bucket_name, filename, expires=expiry
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def delete_file(self, filename: str, bucket: Optional[str] = None) -> bool:
        """Delete file from MinIO"""
        bucket_name = bucket or self.default_bucket
        try:
            self.client.remove_object(bucket_name, filename)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False

    def file_exists(
        self, file_hash: str, extension: str = "", bucket: Optional[str] = None
    ) -> bool:
        """Check if file with given hash exists"""
        bucket_name = bucket or self.default_bucket
        try:
            filename = f"{file_hash}{extension}"
            self.client.stat_object(bucket_name, filename)
            return True
        except S3Error:
            return False

    def get_file_info(
        self, filename: str, bucket: Optional[str] = None
    ) -> Optional[Dict]:
        """Get file metadata"""
        bucket_name = bucket or self.default_bucket
        try:
            stat = self.client.stat_object(bucket_name, filename)
            return {
                "filename": filename,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata,
                "bucket": bucket_name,
            }
        except S3Error as e:
            print(f"Error getting file info: {e}")
            return None

    def download_file(
        self, filename: str, bucket: Optional[str] = None
    ) -> Optional[bytes]:
        """Download file content"""
        bucket_name = bucket or self.default_bucket
        try:
            response = self.client.get_object(bucket_name, filename)
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            print(f"Error downloading file: {e}")
            return None
