# app/core/config.py

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Classe para gerenciar todas as configurações da aplicação.
    Lê automaticamente as variáveis do arquivo .env especificado.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignora campos extras do .env
    )
    
    # --- Configurações Gerais da API ---
    app_env: str = Field('development', alias="APP_ENV")
    app_name: str = Field('API CAEPI', alias="APP_NAME")
    app_version: str = Field('1.0.0', alias="APP_VERSION")
    app_description: str = Field('API CAEPI - Sistema de Consulta', alias="APP_DESCRIPTION")
    debug: bool = Field(False, alias="DEBUG")

    # --- Configurações de Cache ---
    cache_timeout: int = Field(3600, alias="CACHE_TIMEOUT")
    cache_dir: str = Field('cache', alias="CACHE_DIR")
    parquet_file_name: str = Field('ca_certificates.parquet', alias="PARQUET_FILE_NAME")
    enable_parquet_cache: bool = Field(True, alias="ENABLE_PARQUET_CACHE")
    parquet_compression: str = Field('snappy', alias="PARQUET_COMPRESSION")

    # --- Configurações FTP ---
    ftp_host: str = Field(..., alias="FTP_HOST")
    ftp_endpoint: str = Field(..., alias="FTP_ENDPOINT")
    ftp_file_name: str = Field(..., alias="FTP_FILE_NAME")
    ca_file_name: str = Field('tgg_export_caepi.txt', alias="CA_FILE_NAME")

@lru_cache
def get_settings() -> Settings:
    return Settings()