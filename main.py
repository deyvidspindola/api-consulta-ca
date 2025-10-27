import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.interface.routers.certificate_router import router as certificate_router
from app.core.config import get_settings

settings = get_settings()

# Criar aplicação FastAPI com configuração Swagger completa
app = FastAPI(
    title="API CAEPI - Certificados de Aprovação",
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
    1. Use `/certificates/get-certificate-by-ca` para buscar qualquer certificado
    2. Use `/certificates/update-database` para atualizar a base de dados
    """,
    version=settings.app_version,
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
    allow_origins=[settings.cors_origins],  # Em produção, especifique os domínios permitidos
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
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
        "version": settings.app_version
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
        "title": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=settings.reload,
        log_level="info"
    )