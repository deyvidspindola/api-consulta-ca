from app.domain.repositories.ca_repository_interface import CARepositoryInterface


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
                print("Base de certificados atualizada com sucesso")
            else:
                print("Falha ao atualizar base de certificados")
            
            return success
        except Exception as e:
            print(f"Erro ao executar atualização de certificados: {e}")
            return False