from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from app.domain.repositories.logger_interface import LogLevel


@dataclass
class LogEntry:
    """Entidade que representa uma entrada de log"""
    
    level: LogLevel
    message: str
    timestamp: datetime
    component: str
    context: Optional[Dict[str, Any]] = None
    exception: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a entrada de log para dicionário"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "component": self.component,
            "message": self.message,
            "context": self.context or {},
            "exception": self.exception
        }
    
    def __str__(self) -> str:
        """Representação em string do log"""
        context_str = f" | Context: {self.context}" if self.context else ""
        exception_str = f" | Exception: {self.exception}" if self.exception else ""
        
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.level.value} - {self.component} - {self.message}{context_str}{exception_str}"