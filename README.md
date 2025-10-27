# API CAEPI - Certificados de Aprovação

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

**API REST de alta performance** para consulta de Certificados de Aprovação de Equipamentos de Proteção Individual (CA EPI) do Ministério do Trabalho e Emprego (MTE).

Esta API **automatiza e disponibiliza de forma programática** a validação de CAs, eliminando a necessidade de consulta manual no portal oficial, com **cache inteligente**, **logs estruturados** e **observabilidade completa**.

---

## Funcionalidades

### 📋 Core Features
- ✅ **Busca por CA**: Consulta certificados pelo número do registro  
- ✅ **Validação Automática**: Verifica situação (válido/vencido/cancelado)  
- ✅ **Atualização Automática**: Sincroniza com dados do MTPS/CAEPI  
- ✅ **API RESTful**: Respostas padronizadas em JSON estruturado

### 🏗️ Arquitetura & Qualidade
- ✅ **Clean Architecture**  
- ✅ **Domain-Driven Design**  
- ✅ **Dependency Injection**  
- ✅ **Swagger/OpenAPI**

### 🐳 DevOps & Infraestrutura
- ✅ **Docker Multi-stage**  
- ✅ **Debug Remoto (VS Code)**  
- ✅ **Health Checks**  
- ✅ **Auto-restart**

### ⚡ Performance & Cache
- ✅ **Cache Inteligente**: Parquet/Pickle com fallback  
- ✅ **Cache em Memória**: DataFrame otimizado  
- ✅ **Cache Persistente**: Reduz tempo de boot  
- ✅ **Buscas rápidas** com Pandas

### 📊 Observabilidade & Monitoramento
- ✅ **Logs Estruturados** (JSON e texto)  
- ✅ **Log Rotation** (10MB, 5 backups)  
- ✅ **Contexto Enriquecido** (request id, duração, endpoint)  
- ✅ **Níveis Configuráveis** via ENV  
- ✅ **Métricas Prontas**  
- ✅ **Compatível com ELK/Grafana**

---

## 📋 Pré-requisitos

### Para Docker (Recomendado)
- Docker >= 20.10  
- Docker Compose >= 2.0

---

## 🐳 Docker

```bash
# Clone o repositório
git clone https://github.com/deyvidspindola/api-consulta-ca.git
cd api-consulta-ca

# Configurar ambiente
cp .env.example .env

# Desenvolvimento (hot-reload e debug remoto)
docker-compose -f docker-compose.dev.yml up --build

# Produção (otimizada e segura)
docker-compose -f docker-compose.prd.yml up -d --build
```

### 🔧 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose -f docker-compose.dev.yml logs -f

# Rebuild limpo quando necessário
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build

# Executar comandos no container
docker-compose -f docker-compose.dev.yml exec api bash

# Ver logs da aplicação (estruturados)
tail -f logs/app.log | jq   # JSON formatado
tail -f logs/app.log        # Raw
```

### 📊 URLs Disponíveis

| Ambiente | API Base              | Swagger Docs | ReDoc  | Health Check |
|----------|------------------------|--------------|--------|--------------|
| **Dev**  | http://localhost:8400 | /docs        | /redoc | /health      |
| **Prod** | http://localhost:8400 | /docs        | /redoc | /health      |

---

## 🔧 Instalação Local

```bash
# Clone o repositório
git clone https://github.com/deyvidspindola/api-consulta-ca.git
cd api-consulta-ca

# Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o ambiente
cp .env.example .env
# Edite o .env com suas configurações
```

## ▶️ Como Executar

### Com Docker (Recomendado)

```bash
# Desenvolvimento
docker-compose -f docker-compose.dev.yml up --build

# Produção
docker-compose -f docker-compose.prd.yml up -d --build
```

### Localmente

```bash
# Executar a API
python main.py

# Ou usando uvicorn diretamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

---

## 📖 Endpoints

### 🔍 Buscar Certificado
**POST** `/certificates/get-certificate-by-ca`

Busca um certificado específico pelo número do registro CA.

**Request Body:**
```json
{
  "registro_ca": "12345"
}
```

**Response (Encontrado):**
```json
{
  "success": true,
  "message": "Certificado encontrado",
  "data": {
    "registro_ca": "12345",
    "data_validade": "2025-12-31",
    "situacao": "Válido"
  }
}
```

**Response (Não Encontrado):**
```json
{
  "success": false,
  "message": "Certificado não encontrado",
  "data": null
}
```

### 🔄 Atualizar Base de Dados
**POST** `/certificates/update-database`

Atualiza a base de dados com os dados mais recentes do CAEPI.

**Response:**
```json
{
  "success": true,
  "message": "Base de dados atualizada com sucesso",
  "data": null
}
```

### 💚 Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "OK",
  "message": "API funcionando corretamente",
  "version": "1.0.0"
}
```

---

## 🏗️ Arquitetura

O projeto segue os princípios da **Clean Architecture**:

```
app/
├── application/         # Casos de uso (Use Cases)
│   └── use_cases/
├── domain/              # Entidades e interfaces do domínio
│   ├── entities/
│   └── repositories/
├── infrastructure/      # Implementações (repositórios, data sources)
│   ├── cache/
│   ├── datasources/
│   └── repositories/
├── interface/           # Controllers, DTOs, presenters, routers
│   ├── controllers/
│   ├── dtos/
│   ├── presenters/
│   └── routers/
└── core/                # Configurações e utilitários
    ├── config.py
    ├── logging_config.py
    └── middleware.py
```

**Camadas:**
- **Domain**: Regras de negócio e entidades principais  
- **Application**: Casos de uso (orquestração)  
- **Infrastructure**: Acesso a dados externos (FTP, cache, arquivos)  
- **Interface**: Controllers, routers e APIs REST  
- **Core**: Configurações, logging e utilities

---

## 🔧 Tecnologias

### Backend & Framework
- **FastAPI**, **Pydantic**, **Uvicorn**, **Gunicorn**

### Dados & Cache
- **Pandas**, **PyArrow** (Parquet), **Pickle** (fallback)

### DevOps & Observabilidade
- **Docker**, **Logging estruturado**, **Health Checks**

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

---

## Logs e Observabilidade

A API possui **logging dual**:
- **Console**: Formato legível para desenvolvimento  
- **Arquivo**: JSON estruturado para parsing automático

**Exemplo de Log JSON:**
```json
{
  "timestamp": "2025-10-27 18:06:23",
  "level": "INFO",
  "logger": "app.application.use_cases.get_certificate_use_case",
  "message": "Certificado encontrado com sucesso",
  "module": "get_certificate_use_case",
  "function": "execute",
  "line": 39,
  "extras": {
    "certificate_id": "12345",
    "duration_ms": 245.67,
    "endpoint": "/certificates/get-certificate-by-ca"
  }
}
```

**Análise de Logs:**
```bash
# Monitorar logs em tempo real
tail -f logs/app.log

# Analisar com jq (JSON)
cat logs/app.log | jq '.level' | sort | uniq -c

# Buscar erros
grep '"level": "ERROR"' logs/app.log

# Métricas de performance
grep '"duration_ms"' logs/app.log | jq '.extras.duration_ms'
```

**Compatível com:**
- **ELK Stack (Elasticsearch/Logstash/Kibana)**
- **Grafana + Loki**
- **Prometheus** (via parsing)
- **Datadog**, **New Relic**, etc.

---

## Swagger/OpenAPI

A documentação interativa está em **`/docs`** e inclui:
- Descrição de endpoints  
- Exemplos de requests/responses  
- Teste via UI  
- Modelos com validação  
- Tags organizadas

---

## Debug & Desenvolvimento

### Debug Remoto com VS Code

`launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Remote Attach",
      "type": "python",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5681 },
      "pathMappings": [{ "localRoot": "${workspaceFolder}", "remoteRoot": "/app" }]
    }
  ]
}
```

**Comandos:**
```bash
# Executar container em modo debug
docker-compose -f docker-compose.dev.yml up

# Conectar o debugger na porta 5681 (VS Code)
```

---


## Suporte

**Suporte:**
- 📋 Issues: use o sistema de issues do repositório  
- 📖 Documentação: veja `/docs` na API rodando


**Links Úteis:**
- `DOCKER_README.md` – Documentação completa do Docker  
- `docs/LOGGING.md` – Guia de logging e observabilidade  
- Swagger UI: `http://localhost:8400/docs`  
- Repositório CAEPI (MTE): `http://trabalho.gov.br/seguranca-e-saude-no-trabalho/equipamentos-de-protecao-individual-epi`

---

## Changelog

### v1.0.0 (2025-10-27)
- Implementação da Clean Architecture  
- Sistema de cache inteligente Parquet/Pickle  
- Logs estruturados (JSON + texto)  
- Docker multi-stage para dev/prod  
- Debug remoto integrado  
- Observabilidade preparada para ELK/Grafana  
- Documentação Swagger completa  
- Health checks automáticos  
- Performance otimizada

---

*Desenvolvido com ❤️ para automatizar a consulta de Certificados de Aprovação EPI*
