from app.domain.repositories.ca_repository_interface import CARepositoryInterface
from app.infrastructure.datasources.data_source_interface import DataSourceInterface
from app.domain.entities.approve_certificate import ApproveCertificate
from typing import Optional
import pandas as pd


class PandasCARepository(CARepositoryInterface):

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source
        self._index_df: Optional[pd.DataFrame] = None  # índice para buscas rápidas

    async def get_data(self) -> pd.DataFrame:
        """Retorna o DataFrame completo da fonte de dados"""
        return await self.data_source.get_data()
    
    async def _ensure_index(self):
        """Cria índice para consultas rápidas, se ainda não existir"""
        if self._index_df is None:
            df = await self.get_data()
            # Garantir que RegistroCA seja string e sem espaços
            df['RegistroCA'] = df['RegistroCA'].astype(str).str.strip()
            # Criar índice, mantendo coluna RegistroCA no DataFrame
            self._index_df = df.set_index('RegistroCA', drop=False)

    async def get_certificate(self, registro_ca: str) -> Optional[ApproveCertificate]:
        """Busca um certificado específico pelo registro CA usando índice"""
        try:
            await self._ensure_index()
            registro_ca = registro_ca.strip()  # limpar espaços
            
            if registro_ca in self._index_df.index:
                row = self._index_df.loc[registro_ca]
                
                # Se houver duplicatas, pegar a primeira linha
                if isinstance(row, pd.DataFrame):
                    row = row.iloc[0]
                
                return ApproveCertificate(
                    registro_ca=row['RegistroCA'],
                    data_validade=row['DataValidade'],
                    situacao=row['Situacao']
                )
            return None
        except Exception as e:
            print(f"Erro ao buscar certificado {registro_ca}: {e}")
            return None

    async def update_base_certificate(self) -> bool:
        """Atualiza a base de dados dos certificados e reinicia o índice"""
        try:
            success = await self.data_source.update_data()
            if success:
                # Resetar índice para reconstrução com dados novos
                self._index_df = None
            return success
        except Exception as e:
            print(f"Erro ao atualizar base de certificados: {e}")
            return False

    def is_data_available(self) -> bool:
        """Verifica se há dados disponíveis na fonte"""
        return self.data_source.is_data_loaded()

