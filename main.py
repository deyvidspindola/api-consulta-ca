from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.interface.routers.certificate_router import router as certificate_router

# Criar aplicação FastAPI com configuração Swagger completa
app = FastAPI(
    title="🏆 API CAEPI - Certificados de Aprovação",
    description="""
    ## API para consulta de Certificados de Aprovação (CA) do CAEPI
    
    Esta API permite:
    
    * **Buscar certificados** por número do registro CA
    * **Verificar certificados válidos** - apenas certificados ativos
    * **Atualizar base de dados** - sincronizar com dados do MTPS
    
    ### Fonte dos dados
    Os dados são obtidos diretamente do CAEPI (Cadastro de Aprovação de Equipamentos de Proteção Individual) 
    do Ministério do Trabalho e Previdência Social (MTPS).
    
    ### Como usar
    1. Use `/certificates/{registro_ca}` para buscar qualquer certificado
    2. Use `/certificates/update-database` para atualizar a base de dados
    """,
    version="1.0.0",
    contact={
        "name": "Suporte Técnico",
        "email": "suporte@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Certificados",
            "description": "Operações relacionadas aos certificados CA",
        },
        {
            "name": "Sistema",
            "description": "Operações de sistema e monitoramento",
        }
    ]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(certificate_router)

# Health check
@app.get(
    "/health",
    tags=["Sistema"],
    summary="Verificar saúde da API",
    description="Endpoint para verificar se a API está funcionando corretamente"
)
async def health_check():
    """
    Verificação de saúde da API.
    
    Retorna o status atual da aplicação.
    """
    return {
        "status": "OK", 
        "message": "API funcionando corretamente",
        "version": "1.0.0"
    }

@app.get(
    "/",
    tags=["Sistema"],
    summary="Informações da API",
    description="Página inicial com informações básicas da API"
)
async def root():
    """
    Informações básicas da API.
    """
    return {
        "title": "API CAEPI - Certificados de Aprovação",
        "version": "1.0.0",
        "description": "API para consulta de Certificados de Aprovação do CAEPI",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Para desenvolvimento
        log_level="info"
    )