Claro! Aqui está seu conteúdo formatado corretamente como **Markdown (`.md`)**:

````markdown
# 🏆 API CAEPI - Certificados de Aprovação

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

API REST de alta performance e robustez para consulta de Certificados de Aprovação de Equipamentos de Proteção Individual (CA EPI) do Ministério do Trabalho e Emprego (MTE). Esta API automatiza e disponibiliza de forma programática a validação de CAs, eliminando a necessidade de consulta manual no portal oficial.

## 🚀 Funcionalidades

- ✅ **Busca por CA**: Consulta certificados pelo número do registro
- ✅ **Validação**: Verifica apenas certificados válidos/ativos
- ✅ **Atualização**: Sincroniza com dados do MTPS
- ✅ **Swagger**: Documentação interativa completa
- ✅ **Clean Architecture**: Código bem estruturado e testável
- ✅ **Docker**: Containerização para desenvolvimento e produção
- ✅ **Cache**: Redis para otimização de consultas
- ✅ **Logs Estruturados**: Monitoramento e debugging facilitado

## 📋 Pré-requisitos

- Docker e Docker Compose
- Python 3.8+ (para desenvolvimento local)
- Redis (para produção)

## 🐳 Docker - Forma Recomendada

### Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone <url-do-repo>
cd api-consulta-ca

# Inicia o ambiente de dev com rebuild e logs
docker-compose -f docker-compose.dev.yml up --build

# Para rodar em background
docker-compose -f docker-compose.dev.yml up --build -d
````

### Ambiente de Produção

```bash
# Crie o arquivo .env.prod com suas variáveis (veja exemplo abaixo)
cp .env.example .env.prod
# Edite o arquivo .env.prod com suas configurações

# Constrói e inicia a aplicação em modo detached (background)
docker-compose -f docker-compose.prod.yml up --build -d

# Para ver os logs
docker-compose -f docker-compose.prod.yml logs -f

# Para parar e remover os containers
docker-compose -f docker-compose.prod.yml down
```

## 🔧 Instalação Local

```bash
# Clone o repositório
git clone <url-do-repo>
cd api-consulta-ca

# Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

## ▶️ Como Executar

### Com Docker

A API estará disponível em:

* API: [http://localhost:8400](http://localhost:8400)
* Swagger UI: [http://localhost:8400/docs](http://localhost:8400/docs)
* ReDoc: [http://localhost:8400/redoc](http://localhost:8400/redoc)

### Localmente

```bash
# Executar a API
python main.py

# Ou usando uvicorn diretamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em:

* API: [http://localhost:8000](http://localhost:8000)
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📖 Endpoints

### 🔍 Buscar Certificado

`GET /certificates/{registro_ca}`
Busca um certificado específico pelo número do registro CA.

Exemplo:

```bash
curl http://localhost:8400/certificates/12345
```

### 🔄 Atualizar Base de Dados

`POST /certificates/update-database`
Atualiza a base de dados com os dados mais recentes do CAEPI.

Exemplo:

```bash
curl -X POST http://localhost:8400/certificates/update-database
```

### 💚 Health Check

`GET /health`
Verifica se a API está funcionando.

Exemplo de resposta:

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

## 🏗️ Arquitetura

O projeto segue os princípios da Clean Architecture:

```
📁 app/
├── 📁 application/      # Casos de uso (Use Cases)
├── 📁 domain/           # Entidades e interfaces do domínio
├── 📁 infrastructure/   # Implementações (repositórios, data sources)
└── 📁 interface/        # Controllers, DTOs, presenters, routers
```

Camadas:

* **Domain**: Regras de negócio e entidades
* **Application**: Casos de uso da aplicação
* **Infrastructure**: Acesso a dados externos
* **Interface**: Controllers e APIs REST

## 🔧 Tecnologias

* FastAPI: Framework web moderno e rápido
* Pydantic: Validação de dados
* Pandas: Manipulação de dados
* Uvicorn: Servidor ASGI
* Redis: Cache de dados
* Docker: Containerização
* Gunicorn: Servidor WSGI para produção

## 📝 Swagger/OpenAPI

A API possui documentação interativa completa acessível em `/docs`.
Inclui:

* 📋 Descrição detalhada de cada endpoint
* 🔧 Exemplos de requisições e respostas
* 🧪 Interface para testar os endpoints
* 📖 Modelos de dados


## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Exemplo de arquivo `.env`:

```env
# Configurações da API
TITLE=API CAEPI - Certificados de Aprovação
DESCRIPTION=API para consulta de Certificados de Aprovação do CAEPI
VERSION=1.0.0
DEBUG=false

# Configurações de CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Configurações do FTP
FTP_HOST=ftp.mtps.gov.br
FTP_ENDPOINT=portal/fiscalizacao/seguranca-e-saude-no-trabalho/caepi/
FTP_FILE_NAME=tgg_export_caepi.zip

# Configurações de Cache
CACHE_TIMEOUT=3600
REDIS_URL=redis://localhost:6379/0

# Configurações de Segurança
API_KEY=sua-chave-secreta-aqui

# Configurações de Logs
LOG_LEVEL=INFO
```

## 📦 O Que Versionar

✅ Versionar:

* Código-fonte da aplicação
* Arquivos de configuração de exemplo (`.env.example`)
* Documentação
* Dockerfiles e docker-compose files
* Scripts de implantação

❌ Não Versionar:

* Arquivos `.env` com dados sensíveis
* Arquivos de log
* Diretórios `__pycache__`
* Ambientes virtuais (`.venv`, `venv`)
* Arquivos de IDE (`.vscode`, `.idea`)
* Dependências instaladas localmente


## 🐞 Debug no VSCode

Para depurar a API localmente usando o VSCode, você pode configurar o `launch.json` para se conectar ao contêiner ou à aplicação em execução.

Exemplo de configuração:

```json
{
    "name": "Python: Fast",
    "type": "debugpy",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5681
    },
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}/api-consulta-ca",
            "remoteRoot": "/srv"
        }
    ],
    "justMyCode": false
}


## 📞 Suporte

Para dúvidas ou problemas:

* 📧 Email: [deyvid.spindola_ext@sonepar.com.br](mailto:deyvid.spindola_ext@sonepar.com.br)
* 📋 Issues: Use o sistema de issues do repositório

