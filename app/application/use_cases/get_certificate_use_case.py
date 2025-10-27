from typing import Optional
from app.domain.repositories.ca_repository_interface import CARepositoryInterface
from app.domain.entities.approve_certificate import ApproveCertificate
import logging

logger = logging.getLogger(__name__)
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
            logger.warning("Registro CA vazio ou inválido fornecido")
            return None
            
        # Limpar o registro CA (remover espaços, etc.)
        registro_ca_clean = registro_ca.strip()
        logger.info(f"Iniciando busca do certificado: {registro_ca_clean}")
        
        try:
            # Buscar o certificado no repositório
            certificate = await self.ca_repository.get_certificate(registro_ca_clean)
            
            if certificate:
                logger.info(f"Certificado {registro_ca_clean} encontrado com sucesso")
                logger.debug(f"Dados do certificado: {certificate.to_dict()}")
            else:
                logger.info(f"Certificado {registro_ca_clean} não encontrado na base de dados")
            
            return certificate
            
        except Exception as e:
            logger.error(f"Erro ao buscar certificado {registro_ca_clean}: {str(e)}", exc_info=True)
            return None
    