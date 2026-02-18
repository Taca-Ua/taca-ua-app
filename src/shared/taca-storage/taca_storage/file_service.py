import logging
from typing import Optional, Any
from datetime import datetime
from .minio_service import MinioService

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.minio = MinioService()
        self.default_bucket = "taca-ua-files"

    def upload_file(
        self,
        file_data: Any, # Aceita o objeto de arquivo do Django ou FastAPI
        file_name: str,
        content_type: str,
        file_size: int,
    ) -> dict:
        try:
            file_hash, object_name, public_url = self.minio.upload_file(
                file_data=file_data,
                bucket_name=self.default_bucket,
                original_filename=file_name,
                content_type=content_type
            )

            return {
                "file_id": object_name, # nome do objeto (hash + ext)
                "file_name": file_name,
                "file_url": public_url,
                "file_size": file_size,
                "mime_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat() + "Z", 
            }
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {str(e)}")
            raise e

    def delete_file(self, file_id: str) -> bool:
        try:
            self.minio.delete_file(self.default_bucket, file_id)
            return True
        except Exception:
            return False