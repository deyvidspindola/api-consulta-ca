import logging
from app.domain.repositories.ca_repository_interface import CARepositoryInterface

logger = logging.getLogger(__name__)
class UpdateCertificatesUseCase:
    """Caso de uso para atualização da base de certificados"""
    
    def __init__(self, ca_repository: CARepositoryInterface):
        self.ca_repository = ca_repository
    
    async def execute(self) -> bool:
        """
        Atualiza a base de dados de certificados
        
        Returns:
            True se atualização foi bem-sucedida, False caso contrário
        """
        try:
            # Atualizar a base de dados através do repositório
            success = await self.ca_repository.update_base_certificate()
            
            if success:
                logger.info("Base de certificados atualizada com sucesso")
            else:
                logger.warning("Falha ao atualizar base de certificados")

            return success
        except Exception as e:
            logger.error("Erro ao executar atualização de certificados", extra={"error": str(e)})
            return False