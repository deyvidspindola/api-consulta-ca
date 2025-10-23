import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from app.domain.repositories.logger_interface import LoggerInterface, LogLevel
from app.domain.entities.log_entry import LogEntry


class FileLogger(LoggerInterface):
    """Implementação de logger para arquivo com rotação automática"""
    
    def __init__(self, component_name: str, log_file_path: str = "logs/app.log", structured: bool = True, max_file_size_mb: int = 10):
        """
        Args:
            component_name: Nome do componente que está logando
            log_file_path: Caminho para o arquivo de log
            structured: Se True, saída em JSON. Se False, saída legível
            max_file_size_mb: Tamanho máximo do arquivo antes da rotação
        """
        self.component_name = component_name
        self.log_file_path = log_file_path
        self.structured = structured
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
    
    def _rotate_log_if_needed(self) -> None:
        """Rotaciona o log se necessário"""
        if not os.path.exists(self.log_file_path):
            return
            
        if os.path.getsize(self.log_file_path) > self.max_file_size_bytes:
            # Rotacionar arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_path = f"{self.log_file_path}.{timestamp}"
            os.rename(self.log_file_path, rotated_path)
    
    def _log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Método interno para processar o log"""
        self._rotate_log_if_needed()
        
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
            output = json.dumps(log_entry.to_dict(), ensure_ascii=False)
        else:
            # Saída legível
            output = str(log_entry)
        
        # Escrever no arquivo
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(output + "\n")
    
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