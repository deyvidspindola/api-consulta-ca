from app.domain.repositories.ca_repository_interface import CARepositoryInterface
from app.infrastructure.datasources.data_source_interface import DataSourceInterface
from app.domain.entities.approve_certificate import ApproveCertificate
from typing import Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


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
            registro_ca_clean = registro_ca.strip()
            
            logger.debug(f"Buscando certificado: {registro_ca_clean}")
            
            if registro_ca_clean in self._index_df.index:
                row = self._index_df.loc[registro_ca_clean]
                
                # Se houver duplicatas, pegar a primeira linha
                if isinstance(row, pd.DataFrame):
                    row = row.iloc[0]
                    logger.debug(f"Múltiplas entradas encontradas para {registro_ca_clean}, usando a primeira")
                
                # Log dos dados antes da conversão para debug
                logger.debug(f"Dados do certificado: RegistroCA={row['RegistroCA']}, "
                           f"DataValidade={row['DataValidade']} (tipo: {type(row['DataValidade'])}), "
                           f"Situacao={row['Situacao']}")
                
                certificate = ApproveCertificate(
                    registro_ca=str(row['RegistroCA']),
                    data_validade=self._format_date(row['DataValidade']),
                    situacao=str(row['Situacao'])
                )
                
                logger.info(f"Certificado {registro_ca_clean} encontrado com sucesso")
                return certificate
            
            logger.info(f"Certificado {registro_ca_clean} não encontrado")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar certificado {registro_ca}: {e}", exc_info=True)
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
    
    def _format_date(self, date_value) -> str:
        """
        Converte qualquer tipo de data para string no formato esperado.
        
        Args:
            date_value: Valor da data (pode ser Timestamp, string, etc.)
            
        Returns:
            str: Data formatada como string
        """
        try:
            if pd.isna(date_value) or date_value is None:
                return ""
            
            # Se já é string, retornar como está
            if isinstance(date_value, str):
                return date_value.strip()
            
            # Se é Timestamp do pandas, converter para string
            if isinstance(date_value, pd.Timestamp):
                return date_value.strftime("%d/%m/%Y")
            
            # Tentar converter para datetime e depois para string
            if hasattr(date_value, 'strftime'):
                return date_value.strftime("%d/%m/%Y")
            
            # Fallback: converter para string
            return str(date_value)
            
        except Exception as e:
            logger.warning(f"Erro ao formatar data {date_value}: {e}")
            return str(date_value) if date_value is not None else ""

