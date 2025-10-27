import logging
from app.infrastructure.datasources.data_source_interface import DataSourceInterface
from app.infrastructure.cache.parquet_cache import ParquetCacheManager
import pandas as pd
import os
from ftplib import FTP
import io
import zipfile
import time
from app.core.config import get_settings
    
logger = logging.getLogger(__name__)

class CAEPIDataSource(DataSourceInterface):

    def __init__(self):
        self.base_dados_df = None
        self.settings = get_settings()
        self.file_name = self.settings.ca_file_name
        self.base_url = self.settings.ftp_host
        self.endpoint = self.settings.ftp_endpoint
        self.columns_name = [
            "RegistroCA", "DataValidade", "Situacao", "NRProcesso", "CNPJ",
            "RazaoSocial", "Natureza", "NomeEquipamento", "DescricaoEquipamento",
            "MarcaCA", "Referencia", "Cor", "AprovadoParaLaudo", "RestricaoLaudo",
            "ObservacaoAnaliseLaudo", "CNPJLaboratorio", "RazaoSocialLaboratorio",
            "NRLaudo", "Norma"
        ]
        self._cache_timeout = self.settings.cache_timeout
        self._last_update = 0
        
        # Inicializar gerenciador de cache
        self.cache_manager = ParquetCacheManager() if self.settings.enable_parquet_cache else None
        logger.info(f"Cache {'habilitado' if self.cache_manager else 'desabilitado'}")
    
    async def get_data(self) -> pd.DataFrame:
        """
        Obtém os dados com cache inteligente para melhor performance.
        
        Prioridade:
        1. Cache em memória (se válido)
        2. Cache persistente (Parquet/Pickle)
        3. Recarregar do arquivo/FTP
        
        Returns:
            pd.DataFrame: Dados dos certificados CA
        """
        current_time = time.time()
        
        # 1. Verificar cache em memória primeiro
        if (self.base_dados_df is not None and 
            current_time - self._last_update <= self._cache_timeout):
            logger.debug("Retornando dados do cache em memória")
            return self.base_dados_df
        
        # 2. Tentar carregar do cache persistente (muito mais rápido que reprocessar)
        if self.cache_manager and self.cache_manager.is_cache_valid():
            logger.info("Carregando dados do cache persistente")
            cached_df = self.cache_manager.load_from_cache()
            if cached_df is not None:
                self.base_dados_df = cached_df
                self._last_update = current_time
                return self.base_dados_df
        
        # 3. Cache expirado ou não existe - recarregar dados
        logger.info("Cache inválido, recarregando dados do arquivo...")
        await self._to_dataframe()
        self._last_update = current_time
        
        # 4. Salvar no cache persistente para próximas consultas
        if self.cache_manager and self.base_dados_df is not None:
            logger.info("Salvando dados no cache persistente")
            success = self.cache_manager.save_to_cache(self.base_dados_df)
            if success:
                logger.info("Dados salvos no cache com sucesso")
            else:
                logger.warning("Falha ao salvar dados no cache")
        
        return self.base_dados_df

    async def update_data(self) -> bool:
        """
        Atualiza os dados baixando novamente do FTP e invalidando todos os caches.
        
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
        """
        try:
            logger.info("Iniciando atualização de dados...")
            
            # 1. Invalidar cache persistente
            if self.cache_manager:
                self.cache_manager.invalidate_cache()
                logger.info("Cache persistente invalidado")
            
            # 2. Invalidar cache em memória
            self.base_dados_df = None
            self._last_update = 0
            
            # 3. Baixar e processar novos dados
            await self._download_file()
            await self._to_dataframe()
            
            # 4. Salvar no cache persistente
            if self.cache_manager and self.base_dados_df is not None:
                success = self.cache_manager.save_to_cache(self.base_dados_df)
                if success:
                    logger.info("Novos dados salvos no cache")
                else:
                    logger.warning("Falha ao salvar novos dados no cache")
            
            logger.info("Dados atualizados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dados: {e}")
            return False

    async def _load_data(self):
        if not os.path.exists(self.file_name):
            await self._download_file()

    async def _download_file(self):
        """Download do arquivo do FTP com tratamento de erros e backup."""
        file_bkp = f"{self.file_name}.bkp"
        
        # Fazer backup do arquivo atual se existir
        if os.path.exists(self.file_name):
            if os.path.exists(file_bkp):
                os.remove(file_bkp)
            os.rename(self.file_name, file_bkp)
            logger.info("Backup do arquivo atual criado")

        ftp = None
        try:
            logger.info(f"Conectando ao FTP: {self.base_url}")
            ftp = FTP(self.base_url)
            ftp.login()
            ftp.cwd(self.endpoint)
            
            zip_file_name = self.settings.ftp_file_name
            logger.info(f"Baixando arquivo: {zip_file_name}")
            
            r = io.BytesIO()
            ftp.retrbinary(f"RETR {zip_file_name}", r.write)
            
            # Verificar se o download foi bem-sucedido
            if len(r.getvalue()) == 0:
                raise Exception("Arquivo baixado está vazio")
            
            logger.info(f"Arquivo baixado com sucesso: {len(r.getvalue())} bytes")
            
            # Extrair o ZIP
            r.seek(0)  # Voltar para o início do buffer
            with zipfile.ZipFile(r) as zip_file:
                zip_file.extractall()
            
            logger.info("Arquivo extraído com sucesso")
            
            # Remover backup se tudo deu certo
            if os.path.exists(file_bkp):
                os.remove(file_bkp)
                logger.debug("Backup removido")
            
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo: {e}")
            
            # Restaurar backup se existir
            if os.path.exists(file_bkp):
                if os.path.exists(self.file_name):
                    os.remove(self.file_name)
                os.rename(file_bkp, self.file_name)
                logger.info("Backup restaurado devido ao erro")
            
            raise  # Re-lançar a exceção
            
        finally:
            # Fechar conexão FTP
            if ftp:
                try:
                    ftp.quit()
                    logger.debug("Conexão FTP fechada")
                except:
                    logger.warning("Erro ao fechar conexão FTP")
                    pass


    async def _to_dataframe(self):
        """Processa o arquivo e converte para DataFrame com limpeza de dados."""
        try:
            await self._load_data()
            data = await self._read_file()
            logger.info("Arquivo carregado, iniciando processamento")
            
            # Separar as linhas do arquivo
            lines = data.strip().split('\n')
            logger.debug(f"Total de linhas no arquivo: {len(lines)}")
            
            # Remover linhas vazias e limpar espaços
            lines = [line.strip() for line in lines if line.strip()]
            logger.debug(f"Linhas após limpeza: {len(lines)}")
            
            # Lista para armazenar os dados processados
            processed_data = []
            skipped_lines = 0
            
            for i, line in enumerate(lines):
                # Detectar separador automaticamente (primeira tentativa com |, depois ;, depois tab)
                separators = ['|', ';', '\t']
                fields = None
                
                for sep in separators:
                    test_fields = line.split(sep)
                    if len(test_fields) > 1:  # Encontrou um separador válido
                        fields = test_fields
                        break
                
                if fields is None:
                    fields = [line]  # Linha sem separador identificado
                
                # Limpar espaços dos campos
                fields = [field.strip() for field in fields]
                
                if len(fields) >= len(self.columns_name):
                    # Pegar apenas o número de colunas necessárias
                    processed_data.append(fields[:len(self.columns_name)])
                elif len(fields) > 1:  # Linha com alguns campos
                    # Preencher campos faltantes com strings vazias
                    padded_fields = fields + [''] * (len(self.columns_name) - len(fields))
                    processed_data.append(padded_fields[:len(self.columns_name)])
                else:
                    skipped_lines += 1
                    if i < 10:  # Log apenas das primeiras linhas problemáticas
                        logger.debug(f"Linha {i+1} ignorada (poucos campos): {line[:100]}...")
            
            if skipped_lines > 0:
                logger.warning(f"Ignoradas {skipped_lines} linhas com formato inválido")
            
            # Criar o DataFrame
            self.base_dados_df = pd.DataFrame(processed_data, columns=self.columns_name)
            logger.info(f"DataFrame criado com {len(self.base_dados_df)} registros")
            
            # Remover cabeçalho se presente
            if (len(self.base_dados_df) > 0 and 
                self.base_dados_df.iloc[0]['RegistroCA'].upper() in ['NR REGISTRO CA', 'REGISTROCA', 'NUMERO_CA']):
                self.base_dados_df = self.base_dados_df.iloc[1:].reset_index(drop=True)
                logger.info("Cabeçalho removido")
            
            # Limpeza e otimização dos dados
            self._optimize_dataframe()
            
            logger.info(f"Processamento concluído: {len(self.base_dados_df)} certificados carregados")
            return self.base_dados_df
            
        except Exception as e:
            logger.error(f"Erro ao processar dados: {e}")
            raise
    
    def _optimize_dataframe(self):
        """Otimiza o DataFrame para melhor performance."""
        if self.base_dados_df is None or self.base_dados_df.empty:
            return
        
        try:
            # Remover espaços extras de todas as colunas de texto
            string_columns = self.base_dados_df.select_dtypes(include=['object']).columns
            for col in string_columns:
                self.base_dados_df[col] = self.base_dados_df[col].astype(str).str.strip()
            
            # Converter colunas categóricas para economizar memória
            categorical_columns = ['Situacao', 'Natureza', 'MarcaCA', 'Cor', 'AprovadoParaLaudo']
            for col in categorical_columns:
                if col in self.base_dados_df.columns:
                    self.base_dados_df[col] = self.base_dados_df[col].astype('category')
            
            # Tentar converter RegistroCA para numérico se possível
            if 'RegistroCA' in self.base_dados_df.columns:
                try:
                    self.base_dados_df['RegistroCA'] = pd.to_numeric(
                        self.base_dados_df['RegistroCA'], errors='coerce'
                    ).fillna(self.base_dados_df['RegistroCA'])
                except:
                    pass  # Manter como string se conversão falhar
            
            # Tentar converter datas
            if 'DataValidade' in self.base_dados_df.columns:
                try:
                    self.base_dados_df['DataValidade'] = pd.to_datetime(
                        self.base_dados_df['DataValidade'], errors='coerce'
                    )
                except:
                    pass
            
            logger.debug("DataFrame otimizado com sucesso")
            
        except Exception as e:
            logger.warning(f"Erro na otimização do DataFrame: {e}")


    async def _read_file(self):
        try:
            with open(self.file_name, "r", encoding="UTF-8") as file:
                data = file.read()
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo {self.file_name} não encontrado")
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo: {e}")
    
    def is_data_loaded(self) -> bool:
        """Verifica se os dados já foram carregados"""
        return self.base_dados_df is not None and not self.base_dados_df.empty
    
    async def search_certificate_optimized(self, registro_ca: str) -> pd.DataFrame:
        """
        Busca otimizada de certificado usando cache persistente.
        Muito mais rápido que carregar todo o DataFrame.
        
        Args:
            registro_ca: Número do registro CA
            
        Returns:
            pd.DataFrame: Certificado encontrado ou DataFrame vazio
        """
        try:
            # Tentar busca direta no cache persistente (mais eficiente)
            if self.cache_manager and self.cache_manager.is_cache_valid():
                logger.debug(f"Buscando certificado {registro_ca} no cache persistente")
                result = self.cache_manager.search_certificates(registro_ca)
                if result is not None and not result.empty:
                    logger.info(f"Certificado {registro_ca} encontrado no cache")
                    return result
            
            # Fallback para busca tradicional
            logger.debug(f"Buscando certificado {registro_ca} nos dados completos")
            df = await self.get_data()
            if df is not None and not df.empty:
                # Garantir que RegistroCA seja tratado como string para comparação
                result = df[df['RegistroCA'].astype(str).str.strip() == str(registro_ca).strip()]
                return result
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Erro na busca otimizada do certificado {registro_ca}: {e}")
            return pd.DataFrame()
    
    async def search_certificates_by_filters(self, **filters) -> pd.DataFrame:
        """
        Busca avançada com múltiplos filtros usando cache otimizado.
        
        Args:
            **filters: Filtros a aplicar (ex: situacao='VÁLIDO', marca_ca='3M')
            
        Returns:
            pd.DataFrame: Certificados que atendem aos critérios
        """
        try:
            # Mapear nomes de parâmetros para nomes de colunas
            column_mapping = {
                'situacao': 'Situacao',
                'razao_social': 'RazaoSocial',
                'marca_ca': 'MarcaCA',
                'nome_equipamento': 'NomeEquipamento',
                'natureza': 'Natureza',
                'cnpj': 'CNPJ'
            }
            
            # Converter filtros para nomes corretos de colunas
            mapped_filters = {}
            for key, value in filters.items():
                if value:  # Só incluir filtros não vazios
                    column_name = column_mapping.get(key, key)
                    mapped_filters[column_name] = value
            
            # Tentar busca otimizada no cache persistente
            if (self.cache_manager and self.cache_manager.is_cache_valid() and mapped_filters):
                logger.debug(f"Buscando com filtros no cache persistente: {mapped_filters}")
                result = self.cache_manager.search_certificates_by_filters(mapped_filters)
                if result is not None:
                    logger.info(f"Encontrados {len(result)} certificados no cache")
                    return result
            
            # Fallback para busca tradicional
            logger.debug("Buscando com filtros nos dados completos")
            df = await self.get_data()
            if df is None or df.empty:
                return pd.DataFrame()
            
            result = df
            for column, value in mapped_filters.items():
                if column in df.columns:
                    if isinstance(value, str):
                        result = result[result[column].str.contains(value, case=False, na=False)]
                    else:
                        result = result[result[column] == value]
            
            logger.info(f"Encontrados {len(result)} certificados com filtros")
            return result
            
        except Exception as e:
            logger.error(f"Erro na busca com filtros: {e}")
            return pd.DataFrame()
    
    def get_cache_info(self) -> dict:
        """
        Retorna informações sobre o cache para monitoramento.
        
        Returns:
            dict: Informações do cache
        """
        info = {
            "memory_cache": {
                "loaded": self.is_data_loaded(),
                "last_update": self._last_update,
                "cache_timeout": self._cache_timeout,
                "records_count": len(self.base_dados_df) if self.base_dados_df is not None else 0
            },
            "persistent_cache": {
                "enabled": self.cache_manager is not None
            }
        }
        
        if self.cache_manager:
            info["persistent_cache"].update(self.cache_manager.get_cache_stats())
        
        return info
    
    def invalidate_all_caches(self) -> bool:
        """
        Invalida todos os caches (memória e persistente).
        
        Returns:
            bool: True se invalidou com sucesso
        """
        try:
            # Invalidar cache em memória
            self.base_dados_df = None
            self._last_update = 0
            
            # Invalidar cache persistente
            if self.cache_manager:
                success = self.cache_manager.invalidate_cache()
                logger.info("Todos os caches foram invalidados")
                return success
            
            logger.info("Cache em memória invalidado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao invalidar caches: {e}")
            return False