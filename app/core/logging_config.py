import logging
import sys
import os
import json
from logging.handlers import RotatingFileHandler
from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """Formatter personalizado para logs em formato JSON estruturado"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o log record em JSON estruturado
        
        Args:
            record: Log record do Python logging
            
        Returns:
            str: Log formatado em JSON
        """
        # Dados base do log
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread_id": record.thread,
            "process_id": record.process
        }
        
        # Adicionar informações de exceção se existir
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Adicionar campos extras personalizados
        extras = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                'filename', 'module', 'lineno', 'funcName', 'created', 
                'msecs', 'relativeCreated', 'thread', 'threadName', 
                'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 
                'stack_info', 'taskName'
            }:
                extras[key] = value
        
        if extras:
            log_entry["extras"] = extras
        
        # Adicionar contexto da aplicação se disponível
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        if hasattr(record, 'duration'):
            log_entry["duration_ms"] = record.duration
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class LoggingConfigurator:
    """Classe responsável pela configuração completa do sistema de logging"""
    
    def __init__(self):
        self.settings = get_settings()
        self._is_configured = False
    
    def setup_logging(self) -> logging.Logger:
        """
        Configura o sistema de logging da aplicação
        
        Returns:
            logging.Logger: Logger configurado para o módulo principal
        """
        if self._is_configured:
            return logging.getLogger(__name__)
        
        # Definir nível de log
        log_level = getattr(logging, self.settings.log_level.upper(), logging.INFO)
        
        # Criar lista de handlers
        handlers = self._create_handlers()
        
        # Configurar o logger root
        logging.basicConfig(
            level=log_level,
            handlers=handlers,
            force=True  # Força reconfiguração
        )
        
        # Configurar loggers específicos da aplicação
        self._configure_app_loggers()
        
        # Reduzir verbosidade de loggers externos
        self._configure_external_loggers()
        
        self._is_configured = True
        
        # Retornar logger principal
        main_logger = logging.getLogger(__name__)
        self._log_startup_info(main_logger)
        
        return main_logger
    
    def _create_handlers(self) -> list:
        """
        Cria os handlers de logging (console e arquivo)
        
        Returns:
            list: Lista de handlers configurados
        """
        handlers = []
        
        # Handler do console (sempre ativo)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_formatter(is_file=False))
        handlers.append(console_handler)
        
        # Handler de arquivo (se configurado)
        if self.settings.log_to_file:
            file_handler = self._create_file_handler()
            handlers.append(file_handler)
        
        return handlers
    
    def _create_file_handler(self) -> RotatingFileHandler:
        """
        Cria o handler de arquivo com rotação
        
        Returns:
            RotatingFileHandler: Handler configurado para arquivo
        """
        # Garantir que o diretório existe
        log_dir = os.path.dirname(self.settings.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Criar handler com rotação
        file_handler = RotatingFileHandler(
            filename=self.settings.log_file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        file_handler.setFormatter(self._get_formatter(is_file=True))
        
        return file_handler
    
    def _get_formatter(self, is_file: bool) -> logging.Formatter:
        """
        Retorna o formatter apropriado (JSON para arquivo, texto para console)
        
        Args:
            is_file: Se True, retorna formatter JSON; se False, formatter texto
            
        Returns:
            logging.Formatter: Formatter configurado
        """
        if is_file:
            # JSON formatter para arquivo (melhor para parsing automático)
            return JSONFormatter(datefmt='%Y-%m-%d %H:%M:%S')
        else:
            # Formatter simples para console (melhor para leitura humana)
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            return logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    def _configure_app_loggers(self):
        """Configura loggers específicos da aplicação"""
        # Logger da aplicação principal
        app_logger = logging.getLogger("app")
        app_logger.setLevel(logging.DEBUG if self.settings.debug else logging.INFO)
        
        # Loggers específicos por componente
        loggers_config = {
            "app.infrastructure.cache": logging.INFO,
            "app.infrastructure.datasources": logging.INFO,
            "app.infrastructure.repositories": logging.DEBUG if self.settings.debug else logging.INFO,
            "app.application.use_cases": logging.INFO,
            "app.interface.controllers": logging.INFO,
            "uvicorn.access": logging.INFO,
            "uvicorn.error": logging.INFO,
        }
        
        for logger_name, level in loggers_config.items():
            logging.getLogger(logger_name).setLevel(level)
    
    def _configure_external_loggers(self):
        """Reduz a verbosidade de loggers externos"""
        external_loggers = {
            "urllib3": logging.WARNING,
            "httpx": logging.WARNING,
            "asyncio": logging.WARNING,
            "multipart": logging.WARNING,
            "PIL": logging.WARNING,
        }
        
        for logger_name, level in external_loggers.items():
            logging.getLogger(logger_name).setLevel(level)
    
    def _log_startup_info(self, logger: logging.Logger):
        """Log das informações de inicialização"""
        logger.info("🚀 Iniciando aplicação API CAEPI...")
        logger.info(f"📋 Ambiente: {self.settings.app_env}")
        logger.info(f"🐛 Debug: {self.settings.debug}")
        logger.info(f"📝 Log em arquivo: {self.settings.log_to_file}")
        
        if self.settings.log_to_file:
            logger.info(f"📄 Arquivo de log: {self.settings.log_file_path}")
            logger.info("📊 Formato do arquivo: JSON estruturado")
        
        logger.info("📝 Formato do console: Texto legível")
        logger.info(f"🎯 Nível de log: {self.settings.log_level.upper()}")


# Instância global do configurador
_logging_configurator = LoggingConfigurator()


def setup_logging() -> logging.Logger:
    """
    Função pública para configurar o logging
    
    Returns:
        logging.Logger: Logger configurado
    """
    return _logging_configurator.setup_logging()


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para um módulo específico
    
    Args:
        name: Nome do módulo/logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """
    Faz log com contexto adicional (útil para observabilidade)
    
    Args:
        logger: Logger a ser usado
        level: Nível do log (info, error, debug, etc.)
        message: Mensagem do log
        **context: Contexto adicional (request_id, user_id, etc.)
    """
    # Criar LogRecord com contexto adicional
    log_method = getattr(logger, level.lower(), logger.info)
    
    # Adicionar contexto ao record
    for key, value in context.items():
        setattr(logger, key, value)
    
    log_method(message)
    
    # Limpar contexto
    for key in context.keys():
        if hasattr(logger, key):
            delattr(logger, key)