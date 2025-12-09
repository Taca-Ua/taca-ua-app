"""
Storage Service Client
Python client library to interact with the Storage Service API
"""

import os
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException


class StorageServiceClient:
    """Client for interacting with the Storage Service microservice"""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the storage service client

        Args:
            base_url: Base URL of the storage service
                     (defaults to STORAGE_SERVICE_URL env var or http://storage-service:8000)
        """
        self.base_url = (
            base_url or os.getenv("STORAGE_SERVICE_URL", "http://storage-service:8000")
        ).rstrip("/")

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        bucket: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        Upload a file to the storage service

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            bucket: Optional bucket name
            metadata: Optional metadata dictionary

        Returns:
            Dictionary with upload result including hash, url, size, etc.

        Raises:
            RequestException: If the request fails
        """
        try:
            files = {"file": (filename, file_content, content_type)}
            data = {}

            if bucket:
                data["bucket"] = bucket

            if metadata:
                import json

                data["metadata"] = json.dumps(metadata)

            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                data=data,
                timeout=300,  # 5 minutes for large files
            )
            response.raise_for_status()
            return response.json()

        except RequestException as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def download_file(
        self, filename: str, bucket: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Download a file from the storage service

        Args:
            filename: Name of the file to download
            bucket: Optional bucket name

        Returns:
            File content as bytes, or None if not found
        """
        try:
            params: Dict[str, str] = {}
            if bucket:
                params["bucket"] = bucket

            response = requests.get(
                f"{self.base_url}/download/{filename}",
                params=params,
                timeout=300,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.content

        except RequestException as e:
            raise Exception(f"Failed to download file: {str(e)}")

    def get_file_info(
        self, filename: str, bucket: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get file metadata

        Args:
            filename: Name of the file
            bucket: Optional bucket name

        Returns:
            Dictionary with file info, or None if not found
        """
        try:
            params: Dict[str, str] = {}
            if bucket:
                params["bucket"] = bucket

            response = requests.get(
                f"{self.base_url}/info/{filename}",
                params=params,
                timeout=30,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except RequestException as e:
            raise Exception(f"Failed to get file info: {str(e)}")

    def delete_file(self, filename: str, bucket: Optional[str] = None) -> bool:
        """
        Delete a file from storage

        Args:
            filename: Name of the file to delete
            bucket: Optional bucket name

        Returns:
            True if successful, False otherwise
        """
        try:
            params: Dict[str, str] = {}
            if bucket:
                params["bucket"] = bucket

            response = requests.delete(
                f"{self.base_url}/delete/{filename}",
                params=params,
                timeout=30,
            )

            if response.status_code == 404:
                return False

            response.raise_for_status()
            return response.json().get("success", False)

        except RequestException:
            return False

    def file_exists(
        self,
        file_hash: str,
        extension: str = "",
        bucket: Optional[str] = None,
    ) -> bool:
        """
        Check if a file exists by hash

        Args:
            file_hash: SHA256 hash of the file
            extension: File extension
            bucket: Optional bucket name

        Returns:
            True if file exists, False otherwise
        """
        try:
            params: Dict[str, str] = {"extension": extension}
            if bucket:
                params["bucket"] = bucket

            response = requests.get(
                f"{self.base_url}/exists/{file_hash}",
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("exists", False)

        except RequestException:
            return False

    def get_presigned_url(
        self,
        filename: str,
        bucket: Optional[str] = None,
        expiry_hours: int = 1,
    ) -> Optional[str]:
        """
        Get a presigned URL for temporary file access

        Args:
            filename: Name of the file
            bucket: Optional bucket name
            expiry_hours: Number of hours until URL expires

        Returns:
            Presigned URL string, or None if file not found
        """
        try:
            params: Dict[str, Any] = {"expiry_hours": expiry_hours}
            if bucket:
                params["bucket"] = bucket

            response = requests.get(
                f"{self.base_url}/presigned/{filename}",
                params=params,
                timeout=30,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json().get("url")

        except RequestException as e:
            raise Exception(f"Failed to get presigned URL: {str(e)}")

    def health_check(self) -> bool:
        """
        Check if the storage service is healthy

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except RequestException:
            return False
