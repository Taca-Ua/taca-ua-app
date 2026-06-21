import io
import json
import uuid

from config import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from minio import Minio


class MinioService:

    def __init__(self, bucket: str):
        self.base_url = settings.MINIO_SERVICE_URL
        self.bucket = bucket

        self._client = None

    @property
    def client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                self.base_url,
                access_key=settings.MINIO_USER,
                secret_key=settings.MINIO_PASSWORD,
                secure=settings.MINIO_USE_SSL,
            )
            self._ensure_bucket()
        return self._client

    def _ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

        # Ensure bucket policy is set to public read
        self.client.set_bucket_policy(
            self.bucket,
            json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                        }
                    ],
                },
            ),
        )

    def _public_url(self, object_name: str) -> str:
        return f"/files/{self.bucket}/{object_name}"

    def _object_name_from_url(self, url: str) -> str:
        return url.split(f"/{self.bucket}/")[-1]

    def _read_django_file(
        self, file: InMemoryUploadedFile | TemporaryUploadedFile
    ) -> tuple[io.BytesIO, int, str]:
        """Return (stream, size, content_type) from a Django uploaded file."""
        file.seek(0)
        data = file.read()
        return io.BytesIO(data), len(data), file.content_type

    # -------------------------------------------------------------------------

    def upload_file(self, file: InMemoryUploadedFile | TemporaryUploadedFile) -> str:
        """Upload a file from request.FILES and return its public URL."""
        object_name = f"{uuid.uuid4()}_{file.name}"
        stream, size, content_type = self._read_django_file(file)

        self.client.put_object(
            self.bucket,
            object_name,
            data=stream,
            length=size,
            content_type=content_type,
        )
        return self._public_url(object_name)

    def update_file(
        self, url: str, file: InMemoryUploadedFile | TemporaryUploadedFile
    ) -> str:
        """Replace an existing object (by its stored URL) and return the same URL."""
        object_name = self._object_name_from_url(url)
        stream, size, content_type = self._read_django_file(file)

        self.client.put_object(
            self.bucket,
            object_name,
            data=stream,
            length=size,
            content_type=content_type,
        )
        return self._public_url(object_name)

    def delete_file(self, url: str) -> None:
        """Delete a file by its stored URL."""
        object_name = self._object_name_from_url(url)
        self.client.remove_object(self.bucket, object_name)
