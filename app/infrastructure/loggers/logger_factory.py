from typing import Dict, Any, Optional
from app.domain.repositories.logger_interface import LoggerInterface
from app.infrastructure.loggers.console_logger import ConsoleLogger
from app.infrastructure.loggers.file_logger import FileLogger
from app.infrastructure.loggers.elasticsearch_logger import ElasticsearchLogger


class LoggerFactory:
    """Factory para criação de loggers baseado em configuração"""
    
    @staticmethod
    def create_logger(component_name: str, logger_type: str = "console", **kwargs) -> LoggerInterface:
        """
        Cria um logger baseado no tipo especificado
        
        Args:
            component_name: Nome do componente
            logger_type: Tipo do logger ("console", "file", "elasticsearch")
            **kwargs: Argumentos específicos para cada tipo de logger
        
        Returns:
            LoggerInterface: Instância do logger
        
        Raises:
            ValueError: Se o tipo de logger não for suportado
        """
        logger_type = logger_type.lower()
        
        if logger_type == "console":
            structured = kwargs.get("structured", False)  # Por padrão, console legível
            return ConsoleLogger(component_name, structured=structured)
        
        elif logger_type == "file":
            log_file_path = kwargs.get("log_file_path", "logs/app.log")
            structured = kwargs.get("structured", True)  # Por padrão, arquivo estruturado
            max_file_size_mb = kwargs.get("max_file_size_mb", 10)
            return FileLogger(
                component_name,
                log_file_path=log_file_path,
                structured=structured,
                max_file_size_mb=max_file_size_mb
            )
        
        elif logger_type == "elasticsearch":
            elasticsearch_host = kwargs.get("elasticsearch_host", "localhost:9200")
            index_prefix = kwargs.get("index_prefix", "app-logs")
            return ElasticsearchLogger(
                component_name,
                elasticsearch_host=elasticsearch_host,
                index_prefix=index_prefix
            )
        
        else:
            raise ValueError(f"Tipo de logger não suportado: {logger_type}")
    
    @staticmethod
    def create_multiple_loggers(component_name: str, configs: list) -> list[LoggerInterface]:
        """
        Cria múltiplos loggers baseado em uma lista de configurações
        
        Args:
            component_name: Nome do componente
            configs: Lista de configurações de logger
                Exemplo: [
                    {"type": "console", "structured": False},
                    {"type": "file", "log_file_path": "logs/app.log"},
                    {"type": "elasticsearch", "elasticsearch_host": "localhost:9200"}
                ]
        
        Returns:
            list[LoggerInterface]: Lista de loggers criados
        """
        loggers = []
        
        for config in configs:
            logger_type = config.pop("type")
            logger = LoggerFactory.create_logger(component_name, logger_type, **config)
            loggers.append(logger)
        
        return loggers