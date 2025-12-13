"""
MinIO Service for file storage and management
"""

import hashlib
import io
from typing import BinaryIO, Optional

import filetype
from django.conf import settings
from minio import Minio
from minio.error import S3Error


class MinioService:
    """Service for interacting with MinIO storage"""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL,
        )

    def ensure_bucket_exists(self, bucket_name: str) -> None:
        """
        Ensure bucket exists, create if it doesn't

        Args:
            bucket_name: Name of the bucket
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                # Set public read policy for the bucket
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                        }
                    ],
                }
                import json

                self.client.set_bucket_policy(bucket_name, json.dumps(policy))
        except S3Error as e:
            raise Exception(f"Error ensuring bucket exists: {str(e)}")

    def upload_file(
        self,
        file_data: BinaryIO,
        bucket_name: str,
        original_filename: str,
        content_type: Optional[str] = None,
    ) -> tuple[str, str, str]:
        """
        Upload file to MinIO

        Args:
            file_data: File binary data
            bucket_name: Bucket to store the file
            original_filename: Original name of the file
            content_type: MIME type of the file

        Returns:
            Tuple of (file_hash, object_name, public_url)
        """
        # Ensure bucket exists
        self.ensure_bucket_exists(bucket_name)

        # Read file data for hashing
        file_content = file_data.read()
        file_data.seek(0)

        # Calculate SHA256 hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Detect content type if not provided
        if not content_type:
            # Try to detect using filetype
            kind = filetype.guess(file_content)
            if kind is not None:
                content_type = kind.mime
            else:
                # Fallback to generic binary
                content_type = "application/octet-stream"

        # Generate object name (using hash + original extension)
        extension = (
            original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
        )
        object_name = f"{file_hash}.{extension}" if extension else file_hash

        # Upload file
        try:
            self.client.put_object(
                bucket_name,
                object_name,
                io.BytesIO(file_content),
                length=len(file_content),
                content_type=content_type,
            )
        except S3Error as e:
            raise Exception(f"Error uploading file: {str(e)}")

        # Generate public URL
        public_url = self.get_public_url(bucket_name, object_name)

        return file_hash, object_name, public_url

    def get_public_url(self, bucket_name: str, object_name: str) -> str:
        """
        Get public URL for an object

        Args:
            bucket_name: Bucket name
            object_name: Object name

        Returns:
            Public URL
        """
        # For MinIO, construct the URL directly
        protocol = "https" if settings.MINIO_USE_SSL else "http"
        endpoint = settings.MINIO_ENDPOINT
        return f"{protocol}://{endpoint}/{bucket_name}/{object_name}"

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        """
        Delete file from MinIO

        Args:
            bucket_name: Bucket name
            object_name: Object name
        """
        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            raise Exception(f"Error deleting file: {str(e)}")

    def file_exists(self, bucket_name: str, object_name: str) -> bool:
        """
        Check if file exists in bucket

        Args:
            bucket_name: Bucket name
            object_name: Object name

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False
