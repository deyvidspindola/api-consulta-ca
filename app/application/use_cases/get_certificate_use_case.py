from typing import Optional
from app.domain.repositories.ca_repository_interface import CARepositoryInterface
from app.domain.entities.approve_certificate import ApproveCertificate


class GetCertificateUseCase:
    """Caso de uso para busca de certificados por registro CA"""
    
    def __init__(self, ca_repository: CARepositoryInterface):
        self.ca_repository = ca_repository
    
    async def execute(self, registro_ca: str) -> Optional[ApproveCertificate]:
        """
        Busca um certificado por registro CA
        
        Args:
            registro_ca: Número do registro CA a ser buscado
            
        Returns:
            ApproveCertificate ou None se não encontrado
        """
        if not registro_ca or not registro_ca.strip():
            return None
            
        # Limpar o registro CA (remover espaços, etc.)
        registro_ca_clean = registro_ca.strip()
        
        try:
            # Buscar o certificado no repositório
            certificate = await self.ca_repository.get_certificate(registro_ca_clean)
            return certificate
        except Exception as e:
            print(f"Erro ao buscar certificado {registro_ca}: {e}")
            return None
    