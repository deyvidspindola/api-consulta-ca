from app.infrastructure.datasources.data_source_interface import DataSourceInterface
import pandas as pd
import os
from ftplib import FTP
import io
import zipfile

class CAEPIDataSource(DataSourceInterface):

    def __init__(self):
        self.base_dados_df = None
        self.file_name = "tgg_export_caepi.txt"
        self.base_url = "ftp.mtps.gov.br"
        self.endpoint = "portal/fiscalizacao/seguranca-e-saude-no-trabalho/caepi/"
        self.columns_name = [
            "RegistroCA", "DataValidade", "Situacao", "NRProcesso", "CNPJ",
            "RazaoSocial", "Natureza", "NomeEquipamento", "DescricaoEquipamento",
            "MarcaCA", "Referencia", "Cor", "AprovadoParaLaudo", "RestricaoLaudo",
            "ObservacaoAnaliseLaudo", "CNPJLaboratorio", "RazaoSocialLaboratorio",
            "NRLaudo", "Norma"
        ]


    async def get_data(self) -> pd.DataFrame:
        """Retorna o DataFrame, carregando se necessário"""
        if self.base_dados_df is None:
            await self._to_dataframe()
        return self.base_dados_df

    async def update_data(self) -> bool:
        try:
            await self._download_file()
            await self._to_dataframe()
            return True
        except Exception as e:
            print(f"Erro ao atualizar dados: {e}")
            return False

    async def _load_data(self):
        if not os.path.exists(self.file_name):
            await self._download_file()

    async def _download_file(self):
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

        ftp = FTP(self.base_url)
        ftp.login()
        ftp.cwd(self.endpoint)
        
        zip_file_name = "tgg_export_caepi.zip"
        r = io.BytesIO()
        ftp.retrbinary(f"RETR {zip_file_name}", r.write)
        zip_file = zipfile.ZipFile(r)
        zip_file.extractall()
        ftp.quit()


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