import logging
import requests
from typing import Optional, List, Any
from django.core.files.uploadedfile import UploadedFile
from .file_service import FileService

logger = logging.getLogger(__name__)

class RegulationService:
    """
    Service Gateway: Coordena upload para MinIO e persistência no modalities-service.
    Os regulamentos são agora totalmente independentes de modalidades.
    """
    
    BASE_URL = "http://modalities-service:8000/regulations"

    @staticmethod
    def list_regulations() -> List[dict]:
        """Busca a lista de regulamentos: GET /regulations"""
        try:
            response = requests.get(RegulationService.BASE_URL, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar regulamentos: {e}")
            return []

    @staticmethod
    def get_regulation(regulation_id: str) -> dict:
        """Busca um regulamento específico: GET /regulations/{id}"""
        try:
            response = requests.get(f"{RegulationService.BASE_URL}/{regulation_id}", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar regulamento {regulation_id}: {e}")
            raise Exception("Regulamento não encontrado no microserviço.")

    @staticmethod
    def create_regulation(
        title: str, 
        file: UploadedFile, 
        description: Optional[str] = ""
    ) -> dict:
        """Cria um regulamento independente: POST /regulations/internal"""
        file_service = FileService()
        
        upload_data = file_service.upload_file(file)
        
        payload = {
            "title": title,
            "description": description,
            "file_url": upload_data["file_url"]
        }
        
        try:
            response = requests.post(f"{RegulationService.BASE_URL}/internal", json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Rollback no MinIO se o microserviço falhar
            file_service.delete_file(upload_data["file_id"])
            logger.error(f"Erro ao persistir no microserviço: {str(e)}")
            raise Exception(f"Falha na criação do regulamento: {str(e)}")

    @staticmethod
    def delete_regulation(regulation_id: str) -> None:
        """Deleção coordenada: DELETE /regulations/{id}"""
        regulation = RegulationService.get_regulation(regulation_id)
        # Extrai o nome do arquivo da URL para deletar no MinIO
        file_name = regulation['file_url'].split('/')[-1]
        
        try:
            # 1. Deletar no microserviço
            response = requests.delete(f"{RegulationService.BASE_URL}/{regulation_id}", timeout=5)
            response.raise_for_status()
            
            # 2. Deletar no MinIO
            file_service = FileService()
            file_service.delete_file(file_name)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao deletar regulamento: {e}")
            raise Exception("Não foi possível deletar o regulamento.")