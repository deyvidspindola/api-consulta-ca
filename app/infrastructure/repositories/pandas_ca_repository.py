from app.domain.repositories.ca_repository_interface import CARepositoryInterface
from app.infrastructure.datasources.data_source_interface import DataSourceInterface
from app.domain.entities.approve_certificate import ApproveCertificate
from typing import Optional
import pandas as pd


class PandasCARepository(CARepositoryInterface):

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    async def get_data(self) -> pd.DataFrame:
        """Retorna o DataFrame completo da fonte de dados"""
        return await self.data_source.get_data()

    async def get_certificate(self, registro_ca: str) -> Optional[ApproveCertificate]:
        """Busca um certificado específico pelo registro CA"""
        try:
            df = await self.get_data()

            # Buscar o registro no DataFrame
            result = df[df['RegistroCA'] == registro_ca]
            
            if result.empty:
                return None
            
            # Pegar a primeira linha encontrada
            row = result.iloc[0]
            
            # Criar e retornar a entidade ApproveCertificate
            return ApproveCertificate(
                registro_ca=row['RegistroCA'],
                data_validade=row['DataValidade'],
                situacao=row['Situacao']
            )
        except Exception as e:
            print(f"Erro ao buscar certificado {registro_ca}: {e}")
            return None

    async def update_base_certificate(self) -> bool:
        """Atualiza a base de dados dos certificados"""
        try:
            # Usar o método update_data da fonte de dados
            return await self.data_source.update_data()
        except Exception as e:
            print(f"Erro ao atualizar base de certificados: {e}")
            return False

    def is_data_available(self) -> bool:
        """Verifica se há dados disponíveis na fonte"""
        return self.data_source.is_data_loaded()

