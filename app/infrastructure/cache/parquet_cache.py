import pandas as pd
import os
import time
import pickle
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

class ParquetCacheManager:
    """
    Gerenciador de cache em formato otimizado para melhorar a performance
    de leitura e consulta dos dados de certificados CA.
    
    Usa Parquet se pyarrow disponível, senão fallback para Pickle.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.cache_dir = Path(self.settings.cache_dir)
        
        # Verificar se pyarrow está disponível
        try:
            import pyarrow
            self.use_parquet = True
            self.cache_file_path = self.cache_dir / self.settings.parquet_file_name
            logger.info("Usando cache Parquet (pyarrow disponível)")
        except ImportError:
            logger.warning("PyArrow não disponível, usando cache pickle")
            self.use_parquet = False
            self.cache_file_path = self.cache_dir / f"{self.settings.parquet_file_name.replace('.parquet', '.pkl')}"
        
        self.metadata_file_path = self.cache_dir / f"{self.cache_file_path.name}.metadata"
        self.compression = self.settings.parquet_compression if self.use_parquet else 'gzip'
        
        # Criar diretório de cache se não existir
        self.cache_dir.mkdir(exist_ok=True)
    
    def save_to_cache(self, df: pd.DataFrame) -> bool:
        """
        Salva o DataFrame em formato otimizado (Parquet ou Pickle).
        
        Args:
            df: DataFrame com os dados dos certificados
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            if df is None or df.empty:
                logger.warning("DataFrame está vazio, não salvando cache")
                return False
            
            # Otimizações antes de salvar
            df_optimized = self._optimize_dataframe(df)
            
            if self.use_parquet:
                # Salvar em parquet com compressão
                df_optimized.to_parquet(
                    self.cache_file_path,
                    compression=self.compression,
                    index=False,
                    engine='pyarrow'
                )
            else:
                # Salvar em pickle como fallback
                with open(self.cache_file_path, 'wb') as f:
                    pickle.dump(df_optimized, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Salvar metadados
            self._save_metadata(df_optimized)
            
            cache_type = "parquet" if self.use_parquet else "pickle"
            logger.info(f"Cache {cache_type} salvo: {self.cache_file_path}")
            logger.info(f"Registros: {len(df_optimized)}, Tamanho: {self._get_file_size_mb():.2f}MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            return False
    
    def load_from_cache(self) -> Optional[pd.DataFrame]:
        """
        Carrega dados do cache se existir e não estiver expirado.
        
        Returns:
            DataFrame ou None se não existe ou está expirado
        """
        try:
            if not self.is_cache_valid():
                return None
            
            if self.use_parquet:
                df = pd.read_parquet(self.cache_file_path, engine='pyarrow')
            else:
                with open(self.cache_file_path, 'rb') as f:
                    df = pickle.load(f)
            
            cache_type = "parquet" if self.use_parquet else "pickle"
            logger.info(f"Cache {cache_type} carregado: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {e}")
            return None
    
    def is_cache_valid(self) -> bool:
        """
        Verifica se o cache existe e não está expirado.
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not self.cache_file_path.exists():
            return False
        
        # Verificar se não está expirado
        file_time = os.path.getmtime(self.cache_file_path)
        current_time = time.time()
        
        if current_time - file_time > self.settings.cache_timeout:
            logger.info("Cache expirado")
            return False
        
        return True
    
    def invalidate_cache(self) -> bool:
        """
        Remove o cache.
        
        Returns:
            bool: True se removeu com sucesso
        """
        try:
            if self.cache_file_path.exists():
                os.remove(self.cache_file_path)
            
            if self.metadata_file_path.exists():
                os.remove(self.metadata_file_path)
            
            logger.info("Cache invalidado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao invalidar cache: {e}")
            return False
    
    def search_certificates(self, registro_ca: str) -> Optional[pd.DataFrame]:
        """
        Busca certificados específicos no cache de forma otimizada.
        
        Args:
            registro_ca: Número do registro CA para buscar
            
        Returns:
            DataFrame com os resultados ou None se não encontrar
        """
        try:
            df = self.load_from_cache()
            if df is None:
                return None
            
            # Busca otimizada usando query (mais rápido que filtro tradicional)
            result = df.query(f"RegistroCA == '{registro_ca}'")
            
            return result if not result.empty else None
            
        except Exception as e:
            logger.error(f"Erro ao buscar no cache: {e}")
            return None
    
    def search_certificates_by_filters(self, filters: dict) -> Optional[pd.DataFrame]:
        """
        Busca certificados com múltiplos filtros de forma otimizada.
        
        Args:
            filters: Dicionário com os filtros a aplicar
            
        Returns:
            DataFrame com os resultados filtrados
        """
        try:
            df = self.load_from_cache()
            if df is None:
                return None
            
            # Aplicar filtros de forma otimizada
            result = df
            
            for column, value in filters.items():
                if column in df.columns and value:
                    if isinstance(value, str):
                        # Busca case-insensitive para strings
                        result = result[result[column].str.contains(value, case=False, na=False)]
                    else:
                        result = result[result[column] == value]
            
            return result if not result.empty else None
            
        except Exception as e:
            logger.error(f"Erro ao buscar com filtros: {e}")
            return None
    
    def get_cache_stats(self) -> dict:
        """
        Retorna estatísticas do cache.
        
        Returns:
            dict: Estatísticas do cache
        """
        try:
            if not self.cache_file_path.exists():
                return {"cache_exists": False}
            
            # Informações do arquivo
            file_size_mb = self._get_file_size_mb()
            file_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file_path))
            
            # Carregar metadados se existirem
            metadata = self._load_metadata()
            
            return {
                "cache_exists": True,
                "cache_type": "parquet" if self.use_parquet else "pickle",
                "file_path": str(self.cache_file_path),
                "file_size_mb": file_size_mb,
                "last_updated": file_time.isoformat(),
                "is_valid": self.is_cache_valid(),
                "compression": self.compression,
                "total_records": metadata.get("total_records", "N/A"),
                "columns": metadata.get("columns", []),
                "expires_in_seconds": max(0, self.settings.cache_timeout - (time.time() - os.path.getmtime(self.cache_file_path)))
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"cache_exists": False, "error": str(e)}
    
    def _optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Otimiza o DataFrame para melhor performance e compressão.
        """
        df_opt = df.copy()
        
        # Converter colunas de texto para category (economiza memória e espaço)
        categorical_columns = [
            'Situacao', 'Natureza', 'MarcaCA', 'Cor', 
            'AprovadoParaLaudo', 'RestricaoLaudo'
        ]
        
        for col in categorical_columns:
            if col in df_opt.columns:
                df_opt[col] = df_opt[col].astype('category')
        
        # Converter RegistroCA para int se possível (mais eficiente)
        if 'RegistroCA' in df_opt.columns:
            try:
                df_opt['RegistroCA'] = pd.to_numeric(df_opt['RegistroCA'], errors='coerce')
            except:
                pass
        
        # Converter datas se existirem
        if 'DataValidade' in df_opt.columns:
            try:
                df_opt['DataValidade'] = pd.to_datetime(df_opt['DataValidade'], errors='coerce')
            except:
                pass
        
        return df_opt
    
    def _save_metadata(self, df: pd.DataFrame):
        """Salva metadados do cache"""
        try:
            metadata = {
                "total_records": len(df),
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "created_at": datetime.now().isoformat(),
                "compression": self.compression,
                "cache_type": "parquet" if self.use_parquet else "pickle"
            }
            
            import json
            with open(self.metadata_file_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Erro ao salvar metadados: {e}")
    
    def _load_metadata(self) -> dict:
        """Carrega metadados do cache"""
        try:
            if self.metadata_file_path.exists():
                import json
                with open(self.metadata_file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar metadados: {e}")
        
        return {}
    
    def _get_file_size_mb(self) -> float:
        """Retorna o tamanho do arquivo em MB"""
        if self.cache_file_path.exists():
            return os.path.getsize(self.cache_file_path) / (1024 * 1024)
        return 0.0

    # Métodos de compatibilidade com nome antigo
    def save_to_parquet(self, df: pd.DataFrame) -> bool:
        """Método de compatibilidade - redireciona para save_to_cache"""
        return self.save_to_cache(df)
    
    def load_from_parquet(self) -> Optional[pd.DataFrame]:
        """Método de compatibilidade - redireciona para load_from_cache"""
        return self.load_from_cache()