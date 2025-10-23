from app.infrastructure.datasources.data_source_interface import DataSourceInterface
import pandas as pd
import os
from ftplib import FTP
import io
import zipfile
from typing import Optional
from app.domain.repositories.logger_interface import LoggerInterface
from app.infrastructure.loggers.logger_factory import LoggerFactory

class CAEPIDataSource(DataSourceInterface):

    def __init__(self):
        self.base_dados_df = None
        self.file_name = "tgg_export_caepi.txt"
        self.base_url = "ftp.mtps.gov.br"
        self.ftp_user = "anonymous"
        self.endpoint = "portal/fiscalizacao/seguranca-e-saude-no-trabalho/caepi/"
        self.columns_name = [
            "RegistroCA", "DataValidade", "Situacao", "NRProcesso", "CNPJ",
            "RazaoSocial", "Natureza", "NomeEquipamento", "DescricaoEquipamento",
            "MarcaCA", "Referencia", "Cor", "AprovadoParaLaudo", "RestricaoLaudo",
            "ObservacaoAnaliseLaudo", "CNPJLaboratorio", "RazaoSocialLaboratorio",
            "NRLaudo", "Norma"
        ]
        
        # Configurar logging usando nossa arquitetura
        self.logger: LoggerInterface = LoggerFactory.create_logger(
            component_name="CAEPI_DataSource",
            logger_type="file",
            log_file_path="logs/app.log",
            structured=True,  # JSON
            max_file_size_mb=10
        )


    async def get_data(self) -> pd.DataFrame:
        """Retorna o DataFrame, carregando se necessário"""
        if self.base_dados_df is None:
            await self._to_dataframe()
        return self.base_dados_df

    async def update_data(self) -> bool:
        """Atualiza os dados baixando e processando o arquivo"""
        self.logger.info("Iniciando atualização dos dados CAEPI")
        try:
            await self._download_file()
            await self._to_dataframe()
            
            records_count = len(self.base_dados_df) if self.base_dados_df is not None else 0
            self.logger.info("Atualização concluída com sucesso", {"records_loaded": records_count})
            return True
        except Exception as e:
            self.logger.error("Erro ao atualizar dados", {"error": str(e)}, exception=e)
            
            # Tentar usar arquivo existente se disponível
            if os.path.exists(self.file_name) and os.path.getsize(self.file_name) > 0:
                try:
                    await self._to_dataframe()
                    records_count = len(self.base_dados_df) if self.base_dados_df is not None else 0
                    self.logger.warning("Usando dados existentes (versão desatualizada)", {
                        "records_loaded": records_count,
                        "file_size": os.path.getsize(self.file_name)
                    })
                    return True
                except Exception as fallback_error:
                    self.logger.error("Erro ao processar arquivo existente", {"error": str(fallback_error)}, exception=fallback_error)
            
            return False

    async def _load_data(self):
        """Carrega dados verificando se o arquivo existe"""
        if not os.path.exists(self.file_name):
            self.logger.info("Arquivo de dados não encontrado, iniciando download", {"filename": self.file_name})
            await self._download_file()
        else:
            file_size = os.path.getsize(self.file_name)
            self.logger.debug("Arquivo de dados já existe", {"filename": self.file_name, "size_bytes": file_size})

    async def _download_file(self):
        """Baixa o arquivo do FTP com logs detalhados"""
        backup_file = f"{self.file_name}.bak"
        
        # Verificar se arquivo já existe e fazer backup
        if os.path.exists(self.file_name):
            self.logger.debug("Criando backup do arquivo existente", {"filename": self.file_name})
            try:
                os.rename(self.file_name, backup_file)
                self.logger.debug("Backup criado", {"backup_file": backup_file})
            except Exception as e:
                self.logger.error("Erro ao criar backup", {"error": str(e)}, exception=e)
                raise

        ftp = None
        try:
            # Etapa 1: Conectar ao FTP
            self.logger.info("Conectando ao servidor FTP", {"host": self.base_url})
            ftp = FTP(self.base_url)
            ftp.login(user=self.ftp_user)

            # Etapa 2: Navegar para o diretório
            ftp.cwd(self.endpoint)
            self.logger.debug("Conexão FTP estabelecida", {"endpoint": self.endpoint})
            
            # Etapa 3: Baixar arquivo ZIP
            zip_file_name = "tgg_export_caepi.zip"
            self.logger.info("Iniciando download do arquivo", {"filename": zip_file_name})
            
            # Usar um arquivo temporário em vez de BytesIO para arquivos grandes
            temp_zip_path = f"temp_{zip_file_name}"
            try:
                with open(temp_zip_path, 'wb') as temp_file:
                    ftp.retrbinary(f"RETR {zip_file_name}", temp_file.write)
                
                # Verificar tamanho do arquivo baixado
                file_size = os.path.getsize(temp_zip_path)
                self.logger.info("Download concluído", {"file_size_bytes": file_size})
                
                if file_size == 0:
                    raise Exception("Arquivo baixado está vazio")
                
                # Etapa 4: Extrair arquivo ZIP
                self.logger.debug("Iniciando extração do arquivo ZIP")
                
                extracted_successfully = False
                
                # Tentar método 1: zipfile do Python
                try:
                    self.logger.debug("Tentativa de extração com zipfile Python")
                    with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
                        bad_file = zip_file.testzip()
                        if bad_file:
                            raise Exception(f"Arquivo corrompido detectado: {bad_file}")
                        
                        zip_contents = zip_file.namelist()
                        if self.file_name in zip_contents:
                            zip_file.extractall()
                            extracted_successfully = True
                        else:
                            raise Exception(f"Arquivo {self.file_name} não encontrado no ZIP")
                            
                except Exception as e:
                    self.logger.warning("Método zipfile falhou", {"error": str(e)})
                
                # Tentar método 2: 7zip para arquivos corrompidos
                if not extracted_successfully:
                    try:
                        self.logger.debug("Tentativa de extração com 7zip")
                        
                        result = os.system("which 7z > /dev/null 2>&1")
                        if result != 0:
                            raise Exception("7zip não está instalado")
                        
                        extract_command = f"7z x -y '{temp_zip_path}' 2>/dev/null"
                        result = os.system(extract_command)
                        
                        if os.path.exists(self.file_name) and os.path.getsize(self.file_name) > 0:
                            extracted_successfully = True
                        else:
                            raise Exception("7zip não conseguiu extrair arquivo válido")
                            
                    except Exception as e:
                        self.logger.warning("Método 7zip falhou", {"error": str(e)})
                
                # Verificar resultado final
                if extracted_successfully and os.path.exists(self.file_name):
                    extracted_size = os.path.getsize(self.file_name)
                    if extracted_size > 0:
                        self.logger.info("Arquivo extraído com sucesso", {"extracted_size_bytes": extracted_size})
                    else:
                        raise Exception("Arquivo extraído está vazio")
                else:
                    raise Exception("Todas as tentativas de extração falharam")
                    
            finally:
                # Limpar arquivo temporário
                if os.path.exists(temp_zip_path):
                    try:
                        os.remove(temp_zip_path)
                    except Exception as e:
                        self.logger.warning("Erro ao remover arquivo temporário", {"error": str(e)})
            
        except Exception as e:
            self.logger.error("Erro durante o download", {
                "error_type": type(e).__name__,
                "error": str(e)
            }, exception=e)
            
            # Restaurar backup se existir
            if os.path.exists(backup_file):
                try:
                    os.rename(backup_file, self.file_name)
                    
                    # Verificar se temos um arquivo válido para usar
                    if os.path.getsize(self.file_name) > 0:
                        self.logger.warning("Usando arquivo existente (não foi possível baixar nova versão)", {
                            "fallback_file_size": os.path.getsize(self.file_name)
                        })
                        return  # Usar arquivo existente como fallback
                        
                except Exception as restore_error:
                    self.logger.error("Erro ao restaurar backup", {"error": str(restore_error)})
            
            raise  # Re-lançar a exceção para o caller
            
        finally:
            # Fechar conexão FTP
            if ftp:
                try:
                    ftp.quit()
                except Exception as e:
                    self.logger.debug("Erro ao fechar conexão FTP", {"error": str(e)})
            
            # Limpar arquivo de backup se tudo deu certo
            if os.path.exists(backup_file) and os.path.exists(self.file_name):
                try:
                    os.remove(backup_file)
                except Exception as e:
                    self.logger.debug("Erro ao remover backup", {"error": str(e)})


    async def _to_dataframe(self):
        await self._load_data()
        data = await self._read_file()
        
        # Separar as linhas do arquivo
        lines = data.strip().split('\n')
        
        # Remover linhas vazias
        lines = [line for line in lines if line.strip()]
        
        # Lista para armazenar os dados processados
        processed_data = []
        
        for line in lines:
            # Assumindo que os dados estão separados por algum delimitador (ex: tab, vírgula, etc.)
            # Você pode ajustar o separador conforme necessário
            fields = line.split('|')  # Ou use ',' se for CSV, ou outro separador
            
            if len(fields) >= len(self.columns_name):  # Verificar se a linha tem pelo menos todas as colunas necessárias
                processed_data.append(fields[:len(self.columns_name)])  # Pegar todos os campos necessários
            elif len(fields) > 0:  # Se tiver menos campos, preencher com valores vazios
                # Preencher campos faltantes com strings vazias
                padded_fields = fields + [''] * (len(self.columns_name) - len(fields))
                processed_data.append(padded_fields[:len(self.columns_name)])
        
        # Criar o DataFrame
        self.base_dados_df = pd.DataFrame(processed_data, columns=self.columns_name)
        
        # Remover a primeira linha se for cabeçalho
        if len(self.base_dados_df) > 0 and self.base_dados_df.iloc[0]['RegistroCA'] == 'NR Registro CA':
            self.base_dados_df = self.base_dados_df.iloc[1:].reset_index(drop=True)
        
        return self.base_dados_df


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