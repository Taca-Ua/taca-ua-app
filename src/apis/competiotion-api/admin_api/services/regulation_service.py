import logging
from typing import Optional, List
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from ..models import Regulation
from .file_service import FileService

logger = logging.getLogger(__name__)

class RegulationService:
    """
    Service to coordinate Regulation business logic between 
    PostgreSQL and MinIO storage.
    """

    @staticmethod
    def list_regulations() -> List[Regulation]:
        return Regulation.objects.all()

    @staticmethod
    def get_regulation(regulation_id: str) -> Regulation:
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Regulation, id=regulation_id)

    @staticmethod
    def create_regulation(
        title: str, 
        file: UploadedFile, 
        description: Optional[str] = "", 
        modality_id: Optional[str] = None
    ) -> Regulation:
        file_service = FileService()
        
        # 1. Upload para o MinIO via FileService
        upload_data = file_service.upload_file(file)
        
        try:
            # 2. Persistência no banco de dados
            with transaction.atomic():
                regulation = Regulation.objects.create(
                    title=title,
                    description=description,
                    modality_id=modality_id,
                    file_url=upload_data["file_url"]
                )
                return regulation
        except Exception as e:
            # Rollback manual do arquivo no MinIO caso o banco falhe
            file_service.delete_file(upload_data["file_id"])
            logger.error(f"Database error, rolling back MinIO upload: {str(e)}")
            raise e

    @staticmethod
    def delete_regulation(regulation_id: str) -> None:
        regulation = RegulationService.get_regulation(regulation_id)
        file_service = FileService()
        
        # O file_id no seu FileService é o hash do arquivo (nome no MinIO)
        # Extraímos o nome do arquivo da URL para deletar no storage
        file_name = regulation.file_url.split('/')[-1]
        
        with transaction.atomic():
            # 1. Remove do banco
            regulation.delete()
            # 2. Remove do MinIO
            file_service.delete_file(file_name)