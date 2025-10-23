from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class LogLevel(Enum):
    """Níveis de log disponíveis"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerInterface(ABC):
    """Interface abstrata para sistema de logging"""
    
    @abstractmethod
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem informativa"""
        pass
    
    @abstractmethod
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem de aviso"""
        pass
    
    @abstractmethod
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Registra uma mensagem de erro"""
        pass
    
    @abstractmethod
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem de debug"""
        pass
    
    @abstractmethod
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Registra uma mensagem crítica"""
        pass