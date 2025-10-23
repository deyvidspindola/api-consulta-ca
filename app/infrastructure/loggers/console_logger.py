import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from app.domain.repositories.logger_interface import LoggerInterface, LogLevel
from app.domain.entities.log_entry import LogEntry


class ConsoleLogger(LoggerInterface):
    """Implementação de logger para console com saída estruturada"""
    
    def __init__(self, component_name: str, structured: bool = True):
        """
        Args:
            component_name: Nome do componente que está logando
            structured: Se True, saída em JSON. Se False, saída legível
        """
        self.component_name = component_name
        self.structured = structured
    
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
        
        if self.structured:
            # Saída estruturada em JSON
            output = json.dumps(log_entry.to_dict(), ensure_ascii=False, indent=None)
        else:
            # Saída legível
            output = str(log_entry)
        
        # Determinar stream de saída
        stream = sys.stderr if level in [LogLevel.ERROR, LogLevel.CRITICAL] else sys.stdout
        
        print(output, file=stream)
        stream.flush()
    
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