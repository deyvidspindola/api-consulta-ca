# 🐳 Docker Setup - API CAEPI

Este documento descreve como usar a configuração Docker otimizada para a API CAEPI.

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
- ✅ Hot-reload ativado
- ✅ Debug remoto na porta 5681
- ✅ Volume mapeado para alterações em tempo real
- ✅ Logs detalhados
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
- ✅ Usuário não-root para segurança
- ✅ Gunicorn com 4 workers
- ✅ Health check automático
- ✅ Limites de recursos
- ✅ Log rotation
- ✅ Restart automático

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

```bash
# Ver logs em tempo real
docker-compose -f docker-compose.dev.yml logs -f api

# Executar comandos no container
docker-compose -f docker-compose.dev.yml exec api sh

# Rebuildar apenas quando necessário
docker-compose -f docker-compose.dev.yml up --build

# Remover volumes e reconstruir do zero
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
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

## 🐛 Troubleshooting

### Problema: "Port already in use"
```bash
# Verificar processos usando a porta
sudo lsof -i :8400
# Ou parar containers existentes
docker-compose down
```

### Problema: Debug não conecta
- Verifique se a porta 5681 está exposta
- Confirme que o `--wait-for-client` está ativo
- Use `docker-compose logs` para ver se o debugpy iniciou

### Problema: Permissões de arquivo
```bash
# Recriar volumes se necessário
docker-compose down -v
docker-compose up --build
```