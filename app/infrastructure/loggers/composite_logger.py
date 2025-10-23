from typing import List, Optional, Dict, Any
from app.domain.repositories.logger_interface import LoggerInterface


class CompositeLogger(LoggerInterface):
    """
    Logger composto que permite logar para múltiplos destinos simultaneamente
    """
    
    def __init__(self, loggers: List[LoggerInterface]):
        """
        Args:
            loggers: Lista de loggers para usar
        """
        if not loggers:
            raise ValueError("Pelo menos um logger deve ser fornecido")
        
        self.loggers = loggers
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem informativa em todos os loggers"""
        for logger in self.loggers:
            try:
                logger.info(message, context)
            except Exception as e:
                # Se um logger falhar, não deve afetar os outros
                print(f"Erro no logger {type(logger).__name__}: {e}")
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem de aviso em todos os loggers"""
        for logger in self.loggers:
            try:
                logger.warning(message, context)
            except Exception as e:
                print(f"Erro no logger {type(logger).__name__}: {e}")
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Registra uma mensagem de erro em todos os loggers"""
        for logger in self.loggers:
            try:
                logger.error(message, context, exception)
            except Exception as e:
                print(f"Erro no logger {type(logger).__name__}: {e}")
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Registra uma mensagem de debug em todos os loggers"""
        for logger in self.loggers:
            try:
                logger.debug(message, context)
            except Exception as e:
                print(f"Erro no logger {type(logger).__name__}: {e}")
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None) -> None:
        """Registra uma mensagem crítica em todos os loggers"""
        for logger in self.loggers:
            try:
                logger.critical(message, context, exception)
            except Exception as e:
                print(f"Erro no logger {type(logger).__name__}: {e}")
    
    def add_logger(self, logger: LoggerInterface) -> None:
        """Adiciona um novo logger à composição"""
        self.loggers.append(logger)
    
    def remove_logger(self, logger_type: type) -> bool:
        """
        Remove um logger específico da composição
        
        Args:
            logger_type: Tipo do logger a ser removido
            
        Returns:
            bool: True se removido, False se não encontrado
        """
        for i, logger in enumerate(self.loggers):
            if isinstance(logger, logger_type):
                self.loggers.pop(i)
                return True
        return False