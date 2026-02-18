import logging
import uuid
from typing import Optional
from django.core.files.uploadedfile import UploadedFile
from .minio_service import MinioService

from django.utils import timezone

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.minio = MinioService()
        # Definimos um bucket padrão (pode vir de env vars)
        self.default_bucket = "taca-ua-files"

    def upload_file(
        self,
        file: UploadedFile,
        file_type: str = "document",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Upload real para o MinIO integrando a lógica de negócio
        """
        try:
            
            file_hash, object_name, public_url = self.minio.upload_file(
                file_data=file,
                bucket_name=self.default_bucket,
                original_filename=file.name,
                content_type=file.content_type
            )

            return {
                "file_id": file_hash,
                "file_name": file.name,
                "file_url": public_url,
                "file_size": file.size,
                "mime_type": file.content_type,
                "uploaded_at": timezone.now().isoformat(), 
            }
        except Exception as e:
            logger.error(f"Erro ao fazer upload para o MinIO: {str(e)}")
            raise e

    def get_file_url(self, file_id: str) -> str:
        # Se os arquivos forem públicos, o MinioService já gera a URL no upload
        # Caso precise buscar novamente:
        return self.minio.get_public_url(self.default_bucket, file_id)

    def delete_file(self, file_id: str) -> bool:
        try:
            self.minio.delete_file(self.default_bucket, file_id)
            return True
        except Exception:
            return False