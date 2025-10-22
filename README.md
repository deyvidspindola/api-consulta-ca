# 🏆 API CAEPI - Certificados de Aprovação

API para consulta de Certificados de Aprovação (CA) do CAEPI (Cadastro de Aprovação de Equipamentos de Proteção Individual).

## 🚀 Funcionalidades

- ✅ **Busca por CA**: Consulta certificados pelo número do registro
- ✅ **Validação**: Verifica apenas certificados válidos/ativos
- ✅ **Atualização**: Sincroniza com dados do MTPS
- ✅ **Swagger**: Documentação interativa completa
- ✅ **Clean Architecture**: Código bem estruturado e testável

## 📋 Pré-requisitos

- Python 3.8+
- pip

## 🔧 Instalação

```bash
# Clone o repositório
git clone <url-do-repo>
cd api

# Instale as dependências
pip install -r requirements.txt
```

## ▶️ Como executar

```bash
# Executar a API
python main.py

# Ou usando uvicorn diretamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 Endpoints

### 🔍 Buscar Certificado
```http
GET /certificates/{registro_ca}
```
Busca um certificado específico pelo número do registro CA.

**Exemplo:**
```bash
curl http://localhost:8000/certificates/12345
```

### 🔄 Atualizar Base de Dados
```http
POST /certificates/update-database
```
Atualiza a base de dados com os dados mais recentes do CAEPI.

**Exemplo:**
```bash
curl -X POST http://localhost:8000/certificates/update-database
```

### 💚 Health Check
```http
GET /health
```
Verifica se a API está funcionando.

## 📊 Exemplo de Resposta

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

O projeto segue os princípios da **Clean Architecture**:

```
📁 app/
├── 📁 application/      # Casos de uso (Use Cases)
├── 📁 domain/           # Entidades e interfaces do domínio
├── 📁 infrastructure/   # Implementações (repositórios, data sources)
└── 📁 interface/        # Controllers, DTOs, presenters, routers
```

### Camadas:
- **Domain**: Regras de negócio e entidades
- **Application**: Casos de uso da aplicação
- **Infrastructure**: Acesso a dados externos
- **Interface**: Controllers e APIs REST

## 🔧 Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Pydantic**: Validação de dados
- **Pandas**: Manipulação de dados
- **Uvicorn**: Servidor ASGI

## 📝 Swagger/OpenAPI

A API possui documentação interativa completa acessível em `/docs`. 

Inclui:
- 📋 Descrição detalhada de cada endpoint
- 🔧 Exemplos de requisições e respostas
- 🧪 Interface para testar os endpoints
- 📖 Modelos de dados

## 🐛 Logs e Debug

A aplicação possui logs estruturados para facilitar o debug:
- Erros são logados com detalhes
- Operações importantes são rastreadas
- Health checks para monitoramento

## 🔒 Segurança

- CORS configurado
- Validação de entrada com Pydantic
- Tratamento de erros robusto
- Sanitização de parâmetros

## 📞 Suporte

Para dúvidas ou problemas:
- 📧 Email: suporte@example.com
- 📋 Issues: Use o sistema de issues do repositório