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
        """Busca a lista de regulamentos: GET /regulations/"""
        try:
            response = requests.get(f"{RegulationService.BASE_URL}/", timeout=5)
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
            raise Exception(f"Regulamento {regulation_id} não encontrado no microserviço.")

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
            response = requests.post(
                f"{RegulationService.BASE_URL}/internal", 
                json=payload, 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            file_service.delete_file(upload_data["file_id"])
            logger.error(f"Erro ao persistir regulamento no microserviço: {str(e)}")
            raise Exception(f"Falha na criação do regulamento: {str(e)}")

    @staticmethod
    def delete_regulation(regulation_id: str) -> None:
        """Deleção coordenada: Remove no microserviço e depois no MinIO"""
        try:
            regulation = RegulationService.get_regulation(regulation_id)
            file_name = regulation['file_url'].split('/')[-1]
            
            response = requests.delete(f"{RegulationService.BASE_URL}/{regulation_id}", timeout=5)
            response.raise_for_status()
            
            file_service = FileService()
            file_service.delete_file(file_name)
            
            logger.info(f"Regulamento {regulation_id} e ficheiro {file_name} removidos com sucesso.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro no processo de deleção do regulamento {regulation_id}: {e}")
            raise Exception("Não foi possível completar a remoção do regulamento.")