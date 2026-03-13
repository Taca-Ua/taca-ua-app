import logging
from typing import Optional
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone

from taca_storage import FileService as SharedFileService

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        # Instanciamos o serviço do pacote compartilhado
        self.shared_service = SharedFileService()

    def upload_file(
        self,
        file: UploadedFile,
        file_type: str = "document",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Adaptador para Django que utiliza o serviço de storage compartilhado.
        """
        try:
            # Delegamos o upload para o pacote shared
            # Passamos os atributos brutos do arquivo que o shared entende
            result = self.shared_service.upload_file(
                file_data=file,
                file_name=file.name,
                content_type=file.content_type,
                file_size=file.size
            )
            
            # Mantemos o retorno compatível com o que a sua View espera,
            # mas agora os dados vêm do motor universal.
            return {
                "file_id": result["file_id"],
                "file_name": result["file_name"],
                "file_url": result["file_url"],
                "file_size": result["file_size"],
                "mime_type": result["mime_type"],
                "uploaded_at": timezone.now().isoformat(), # Mantemos o timezone do Django aqui
            }
        except Exception as e:
            logger.error(f"Erro no adaptador de upload: {str(e)}")
            raise e

    def get_file_url(self, file_id: str) -> str:
        # O file_id aqui é o nome do objeto (hash.extensao)
        return self.shared_service.minio.get_public_url(
            self.shared_service.default_bucket, 
            file_id
        )

    def delete_file(self, file_id: str) -> bool:
        """
        Deleta o arquivo usando o motor compartilhado.
        """
        return self.shared_service.delete_file(file_id)