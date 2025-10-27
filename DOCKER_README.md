# 🐳 Docker Setup - API CAEPI

Este documento descreve como usar a configuração Docker **otimizada e production-ready** para a API CAEPI, com suporte a **debug remoto**, **logs estruturados** e **observabilidade completa**.

## 📋 Pré-requisitos

- Docker >= 20.10
- Docker Compose >= 2.0
- Arquivo `.env` configurado (copie de `.env.example`)

## 🚀 Como usar

### Desenvolvimento Local (com Debug)

```bash
# Construir e iniciar o ambiente de desenvolvimento
docker-compose -f docker-compose.dev.yml up --build

# Ou em background
docker-compose -f docker-compose.dev.yml up -d --build

# Parar o ambiente
docker-compose -f docker-compose.dev.yml down
```

**Características do ambiente de desenvolvimento:**
- ✅ **Hot-reload** ativado (código atualiza automaticamente)
- ✅ **Debug remoto** na porta 5681 (VS Code integrado)
- ✅ **Volume mapeado** para alterações em tempo real
- ✅ **Logs estruturados** (console legível + arquivo JSON)
- ✅ **Cache inteligente** (Parquet/Pickle com fallback)
- ✅ **Observabilidade** preparada (métricas, contexto enriquecido)
- ✅ API disponível em: http://localhost:8400

### Produção

```bash
# Construir e iniciar o ambiente de produção
docker-compose -f docker-compose.prd.yml up -d --build

# Verificar logs
docker-compose -f docker-compose.prd.yml logs -f

# Parar o ambiente
docker-compose -f docker-compose.prd.yml down
```

**Características do ambiente de produção:**
- ✅ **Usuário não-root** para segurança máxima
- ✅ **Gunicorn** com 4 workers otimizados
- ✅ **Health check** automático a cada 30s
- ✅ **Limites de recursos** definidos
- ✅ **Log rotation** automática (10MB, 5 backups)
- ✅ **Restart automático** em caso de falha
- ✅ **Cache persistente** entre restarts
- ✅ **Logs JSON estruturados** para parsing automático

## 🔧 Debug Remoto (VS Code)

Para usar o debug remoto no VS Code, adicione esta configuração em `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5681
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ]
        }
    ]
}
```

## 🌐 Endpoints Disponíveis

- **API Docs**: http://localhost:8400/docs
- **ReDoc**: http://localhost:8400/redoc
- **Health Check**: http://localhost:8400/health

## 🛠️ Comandos Úteis

### Logs & Monitoramento
```bash
# Ver logs em tempo real
docker-compose -f docker-compose.dev.yml logs -f api

# Logs estruturados da aplicação
tail -f logs/app.log | jq          # JSON formatado
tail -f logs/app.log               # Raw
grep "ERROR" logs/app.log          # Apenas erros
grep "certificate" logs/app.log    # Logs de certificados

# Métricas de performance
grep '"duration_ms"' logs/app.log | jq '.extras.duration_ms'
```

### Desenvolvimento
```bash
# Executar comandos no container
docker-compose -f docker-compose.dev.yml exec api bash

# Rebuild quando necessário
docker-compose -f docker-compose.dev.yml up --build

# Rebuild limpo (remove cache)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build

# Ver status dos containers
docker-compose -f docker-compose.dev.yml ps

# Ver uso de recursos
docker stats api-consulta-ca-api-1
```

### Debug & Troubleshooting
```bash
# Conectar ao container em execução
docker exec -it api-consulta-ca-api-1 bash

# Verificar logs de erro específicos
docker logs api-consulta-ca-api-1 | grep ERROR

# Testar endpoint de health
curl http://localhost:8400/health

# Ver configurações ativas
docker exec api-consulta-ca-api-1 env | grep -E "(LOG_|CACHE_|DEBUG)"
```

## 📁 Estrutura dos Arquivos Docker

```
├── Dockerfile              # Multi-stage: development e production
├── docker-compose.dev.yml  # Configuração para desenvolvimento
├── docker-compose.prd.yml  # Configuração para produção
├── .dockerignore           # Arquivos ignorados no build
├── .env.example            # Exemplo de variáveis de ambiente
└── .env                    # Suas variáveis de ambiente (não commitado)
```

## 🔒 Segurança

- ✅ Multi-stage build para imagens menores
- ✅ Usuário não-root em produção
- ✅ Configuração `no-new-privileges`
- ✅ Limites de recursos definidos
- ✅ Health checks configurados
- ✅ Variáveis de ambiente isoladas

## � Observabilidade & Monitoramento

### Logs Estruturados
A aplicação gera logs em **dois formatos**:
- **Console**: Texto legível para desenvolvimento
- **Arquivo**: JSON estruturado para parsing automático

#### Exemplo de Log JSON:
```json
{
  "timestamp": "2025-10-27 18:06:23",
  "level": "INFO",
  "logger": "app.application.use_cases.get_certificate_use_case",
  "message": "Certificado encontrado com sucesso",
  "extras": {
    "certificate_id": "12345",
    "duration_ms": 245.67,
    "endpoint": "/certificates/get-certificate-by-ca"
  }
}
```

### Análise de Performance
```bash
# Métricas básicas dos logs
cat logs/app.log | jq '.level' | sort | uniq -c

# Performance por endpoint
grep '"duration_ms"' logs/app.log | jq '.extras.duration_ms' | sort -n

# Taxa de cache hit/miss
grep '"cache_type"' logs/app.log | jq '.extras.cache_type' | sort | uniq -c

# Certificados encontrados vs não encontrados
grep "encontrado" logs/app.log | wc -l
```

### Integração com Ferramentas de Observabilidade

#### ELK Stack (Elasticsearch + Logstash + Kibana)
```yaml
version: '3.8'
services:
  api:
    # sua API aqui
    
  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logs:/logs:ro
    # Processa logs/app.log
    
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    
  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
```

#### Grafana + Loki
```yaml
version: '3.8'
services:
  api:
    # sua API aqui
    
  loki:
    image: grafana/loki:2.9.0
    
  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./logs:/var/log:ro
    # Coleta logs/app.log
    
  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3000:3000"
```

## �🐛 Troubleshooting

### Problema: "Port already in use"
```bash
# Verificar processos usando a porta
sudo lsof -i :8400
# Ou parar containers existentes
docker-compose down
```

### Problema: Debug não conecta
```bash
# Verificar se a porta 5681 está exposta
docker port api-consulta-ca-api-1

# Ver logs do debugpy
docker logs api-consulta-ca-api-1 | grep debugpy

# Testar conexão manual
telnet localhost 5681
```

### Problema: Cache não funcionando
```bash
# Verificar configuração de cache
docker exec api-consulta-ca-api-1 env | grep CACHE

# Ver logs de cache
grep '"cache"' logs/app.log

# Limpar cache e rebuildar
docker-compose down -v
docker-compose up --build
```

### Problema: Logs não aparecem
```bash
# Verificar configuração de logging
docker exec api-consulta-ca-api-1 env | grep LOG

# Verificar permissões do diretório
ls -la logs/

# Recriar diretório de logs
sudo rm -rf logs/ && mkdir logs && chmod 755 logs
```

### Problema: Performance lenta
```bash
# Verificar uso de recursos
docker stats api-consulta-ca-api-1

# Ver logs de performance
grep '"duration_ms"' logs/app.log | tail -10

# Verificar cache hit rate
grep '"cache_type"' logs/app.log | tail -20
```