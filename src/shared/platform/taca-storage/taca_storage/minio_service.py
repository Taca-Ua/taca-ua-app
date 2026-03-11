"""
Shared MinIO Service for file storage and management.
Universal implementation for Django and FastAPI.
"""

import hashlib
import io
import os
import json
from typing import BinaryIO, Optional

import filetype
from minio import Minio
from minio.error import S3Error


class MinioService:
    """Service for interacting with MinIO storage across TACA microservices"""

    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ROOT_USER", "admin")
        self.secret_key = os.getenv("MINIO_ROOT_PASSWORD", "adminadmin")
        self.secure = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
        self.public_endpoint = os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost/files")

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    def ensure_bucket_exists(self, bucket_name: str) -> None:
        """Ensure bucket exists and set public read policy"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                
                # Política de leitura pública para o bucket
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
        """Upload file and return (file_hash, object_name, public_url)"""
        self.ensure_bucket_exists(bucket_name)

        file_content = file_data.read()
        file_data.seek(0)

        file_hash = hashlib.sha256(file_content).hexdigest()

        if not content_type:
            kind = filetype.guess(file_content)
            content_type = kind.mime if kind else "application/octet-stream"

        extension = (
            original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
        )
        object_name = f"{file_hash}.{extension}" if extension else file_hash

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

        public_url = self.get_public_url(bucket_name, object_name)
        return file_hash, object_name, public_url

    def get_public_url(self, bucket_name: str, object_name: str) -> str:
        """Generate the public URL based on the environment configuration"""
        if self.public_endpoint:
            return f"{self.public_endpoint.rstrip('/')}/{bucket_name}/{object_name}"
        
        # Fallback caso a variável não exista
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.endpoint}/{bucket_name}/{object_name}"

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            raise Exception(f"Error deleting file: {str(e)}")

    def file_exists(self, bucket_name: str, object_name: str) -> bool:
        """Check if file exists"""
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False