# Sistema de Logging - API Consulta CA

## 📋 Visão Geral

Sistema de logging modular e extensível seguindo os princípios de Clean Architecture. Permite facilmente trocar implementações (console, arquivo, Elasticsearch) sem alterar o código que usa o logger.

## 🏗️ Arquitetura

```
Domain Layer (Abstrações)
├── LoggerInterface - Interface abstrata
└── LogEntry - Entidade de log

Infrastructure Layer (Implementações)
├── ConsoleLogger - Log para console
├── FileLogger - Log para arquivo com rotação
├── ElasticsearchLogger - Log para Elasticsearch
├── CompositeLogger - Log para múltiplos destinos
└── LoggerFactory - Factory para criar loggers
```

## 🚀 Como Usar

### 1. Logger Básico (Console)

```python
from app.infrastructure.loggers.logger_factory import LoggerFactory

# Logger simples para console (legível)
logger = LoggerFactory.create_logger(
    component_name="MeuComponente",
    logger_type="console",
    structured=False
)

logger.info("Aplicação iniciada")
logger.error("Erro na conexão", {"host": "localhost"}, exception)
```

### 2. Logger para Arquivo

```python
# Logger para arquivo com rotação
logger = LoggerFactory.create_logger(
    component_name="MeuComponente",
    logger_type="file",
    log_file_path="logs/app.log",
    structured=True,  # JSON
    max_file_size_mb=10
)

logger.info("Dados processados", {"records": 150})
```

### 3. Logger Composto (Múltiplos Destinos)

```python
from app.infrastructure.loggers.composite_logger import CompositeLogger

console_logger = LoggerFactory.create_logger("App", "console")
file_logger = LoggerFactory.create_logger("App", "file")

# Log vai para console E arquivo
composite = CompositeLogger([console_logger, file_logger])
composite.info("Mensagem importante")
```

### 4. Logger para Elasticsearch

```python
# Requer: pip install elasticsearch
logger = LoggerFactory.create_logger(
    component_name="MeuComponente",
    logger_type="elasticsearch",
    elasticsearch_host="localhost:9200",
    index_prefix="app-logs"
)

logger.info("Sistema iniciado", {"version": "1.0.0"})
```

## 📊 Níveis de Log

- **DEBUG**: Informações detalhadas para debugging
- **INFO**: Informações gerais do funcionamento
- **WARNING**: Avisos que não impedem funcionamento
- **ERROR**: Erros que podem afetar funcionalidades
- **CRITICAL**: Erros críticos que podem parar o sistema

## 📝 Formato das Mensagens

### Console (Estruturado = False)
```
[2025-10-23 14:30:15] INFO - MeuComponente - Processando dados | Context: {"records": 150}
```

### Arquivo/Elasticsearch (Estruturado = True)
```json
{
  "timestamp": "2025-10-23T14:30:15.123456",
  "level": "INFO",
  "component": "MeuComponente",
  "message": "Processando dados",
  "context": {"records": 150},
  "exception": null
}
```

## 🔧 Boas Práticas

### 1. Mensagens Objetivas
```python
# ✅ Bom
logger.info("Dados carregados", {"records": 150, "duration_ms": 250})

# ❌ Ruim
logger.info("🎉 Yeahh! Os dados foram carregados com muito sucesso!!!")
```

### 2. Use Contexto para Dados Estruturados
```python
# ✅ Bom
logger.error("Falha na conexão", {"host": "db.example.com", "port": 5432}, exception)

# ❌ Ruim  
logger.error(f"Falha na conexão com {host}:{port} - {str(exception)}")
```

### 3. Níveis Apropriados
```python
logger.debug("Cache hit", {"key": "user_123"})        # Detalhes técnicos
logger.info("Usuario logado", {"user_id": 123})       # Eventos importantes
logger.warning("Cache expirado", {"key": "session"})  # Problemas não críticos
logger.error("Query falhou", {"sql": query})          # Erros funcionais
logger.critical("Database offline", {"host": "db1"})  # Sistema comprometido
```

## 🔄 Extensibilidade

Para adicionar novo tipo de logger:

1. **Implemente LoggerInterface**:
```python
from app.domain.repositories.logger_interface import LoggerInterface

class MeuCustomLogger(LoggerInterface):
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        # Sua implementação
        pass
    # ... outros métodos
```

2. **Atualize LoggerFactory**:
```python
# Em logger_factory.py
elif logger_type == "meu_custom":
    return MeuCustomLogger(component_name, **kwargs)
```

## 📁 Exemplo de Uso Completo

Veja `exemplo_logging.py` para demonstrações práticas de todos os tipos de logger.

## 🔗 Integração com Componentes Existentes

O `CAEPIDataSource` já foi refatorado para usar o novo sistema:

```python
# Antes (logging manual)
self.logger = logging.getLogger(__name__)

# Depois (sistema novo)
self.logger = LoggerFactory.create_logger(
    component_name="CAEPI_DataSource",
    logger_type="console",
    structured=False
)
```