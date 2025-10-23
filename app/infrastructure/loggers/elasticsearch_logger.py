import json
from datetime import datetime
from typing import Optional, Dict, Any
from app.domain.repositories.logger_interface import LoggerInterface, LogLevel
from app.domain.entities.log_entry import LogEntry


class ElasticsearchLogger(LoggerInterface):
    """
    Implementação de logger para Elasticsearch
    Nota: Requer instalação do elasticsearch-py (pip install elasticsearch)
    """
    
    def __init__(self, component_name: str, elasticsearch_host: str = "localhost:9200", index_prefix: str = "app-logs"):
        """
        Args:
            component_name: Nome do componente que está logando
            elasticsearch_host: Host do Elasticsearch
            index_prefix: Prefixo do índice (será app-logs-YYYY-MM)
        """
        self.component_name = component_name
        self.elasticsearch_host = elasticsearch_host
        self.index_prefix = index_prefix
        self._es_client = None
        
        # Tentar importar e inicializar cliente Elasticsearch
        try:
            from elasticsearch import Elasticsearch
            self._es_client = Elasticsearch([elasticsearch_host])
        except ImportError:
            print("⚠️ Elasticsearch client não instalado. Use: pip install elasticsearch")
        except Exception as e:
            print(f"⚠️ Erro ao conectar no Elasticsearch: {e}")
    
    def _get_index_name(self) -> str:
        """Gera nome do índice baseado na data atual"""
        return f"{self.index_prefix}-{datetime.now().strftime('%Y-%m')}"
    
    def _log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Método interno para processar o log"""
        log_entry = LogEntry(
            level=level,
            message=message,
            timestamp=datetime.now(),
            component=self.component_name,
            context=context,
            exception=str(exception) if exception else None
        )
        
        # Se não há cliente ES, usar fallback para console
        if not self._es_client:
            print(f"[ES-FALLBACK] {log_entry}")
            return
        
        try:
            # Enviar para Elasticsearch
            doc = log_entry.to_dict()
            self._es_client.index(
                index=self._get_index_name(),
                body=doc
            )
        except Exception as e:
            # Fallback para console se ES falhar
            print(f"[ES-ERROR] Falha ao enviar log para ES: {e}")
            print(f"[ES-FALLBACK] {log_entry}")
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem informativa"""
        self._log(LogLevel.INFO, message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem de aviso"""
        self._log(LogLevel.WARNING, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Registra uma mensagem de erro"""
        self._log(LogLevel.ERROR, message, context, exception)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem de debug"""
        self._log(LogLevel.DEBUG, message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Registra uma mensagem crítica"""
        self._log(LogLevel.CRITICAL, message, context, exception)