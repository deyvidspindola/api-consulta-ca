# app/core/config.py

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Classe para gerenciar todas as configurações da aplicação.
    Lê automaticamente as variáveis do arquivo .env especificado.
    """
    
    # --- Configurações Gerais da API ---
    title: str = Field(default="API CAEPI", env="TITLE")
    description: str = Field(default="...", env="DESCRIPTION")
    version: str = Field(default="1.0.0", env="VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # --- Configurações da Fonte de Dados (FTP) ---
    ftp_host: str = Field(..., env="FTP_HOST")
    ftp_endpoint: str = Field(..., env="FTP_ENDPOINT")
    ftp_file_name: str = Field(..., env="FTP_FILE_NAME")

    # --- Configurações de Cache ---
    cache_timeout: int = Field(default=3600, env="CACHE_TIMEOUT")

    # --- Configurações de Segurança (para quando implementar) ---
    # api_key: str = Field(..., env="API_KEY")
    # allowed_origins: List[str] = Field(default=[], env="ALLOWED_ORIGINS")

    class Config:
        # Define o nome do arquivo .env a ser carregado
        env_file = ".env"
        # Permite que o Pydantic leia variáveis de ambiente mesmo que não estejam no arquivo .env
        case_sensitive = False

# Cria uma instância única das configurações para ser usada em toda a aplicação
settings = Settings()