from fastapi import APIRouter, HTTPException, Depends
from app.interface.controllers.certificate_controller import CertificateController
from app.interface.presenters.certificate_presenter import CertificatePresenter
from app.infrastructure.repositories.pandas_ca_repository import PandasCARepository
from app.infrastructure.datasources.caepi_data_source import CAEPIDataSource
from app.application.use_cases.get_certificate_use_case import GetCertificateUseCase
from app.application.use_cases.update_certificates_use_case import UpdateCertificatesUseCase
from app.interface.dtos.certificate_dto import ApiResponse, CertificateRequest

# Criar router
router = APIRouter(
    prefix="/certificates",
    tags=["Certificados"],
    responses={
        404: {"description": "Certificado não encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)


async def get_certificate_controller() -> CertificateController:
    """Dependency injection para o controller"""
    # Criar instâncias das dependências
    data_source = CAEPIDataSource()
    repository = PandasCARepository(data_source)
    presenter = CertificatePresenter()
    
    # Criar use cases
    get_certificate_use_case = GetCertificateUseCase(repository)
    update_certificates_use_case = UpdateCertificatesUseCase(repository)
    
    return CertificateController(
        get_certificate_use_case=get_certificate_use_case,
        update_certificates_use_case=update_certificates_use_case,
        presenter=presenter
    )


@router.post(
    "/get-certificate-by-ca",
    response_model=ApiResponse,
    summary="Buscar certificado por CA",
    description="Busca um certificado específico pelo número do registro CA",
    responses={
        200: {
            "description": "Certificado encontrado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Certificado encontrado",
                        "data": {
                            "registro_ca": "12345",
                            "data_validade": "2025-12-31",
                            "situacao": "Válido"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Certificado não encontrado"
        },
        422: {
            "description": "Dados de entrada inválidos"
        }
    }
)
async def get_certificate(
    request: CertificateRequest,
    controller: CertificateController = Depends(get_certificate_controller)
):
    """
    Busca um certificado pelo registro CA.
    
    Recebe no corpo da requisição:
    - **registro_ca**: Número do registro do Certificado de Aprovação
    
    Exemplo de requisição:
    ```json
    {
        "registro_ca": "12345"
    }
    ```
    """
    result = await controller.get_certificate(request.registro_ca)
    
    if not result.success:
        if "não encontrado" in result.message:
            raise HTTPException(status_code=404, detail=result.message)
        else:
            raise HTTPException(status_code=500, detail=result.message)
    
    return result

@router.post(
    "/update-database",
    response_model=ApiResponse,
    summary="Atualizar base de dados",
    description="Atualiza a base de dados de certificados com os dados mais recentes",
    responses={
        200: {
            "description": "Base de dados atualizada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Atualização realizada",
                        "data": None
                    }
                }
            }
        }
    }
)
async def update_database(
    controller: CertificateController = Depends(get_certificate_controller)
):
    """
    Atualiza a base de dados de certificados.
    
    Este endpoint baixa os dados mais recentes do CAEPI e atualiza
    a base de dados local para garantir informações atualizadas.
    """
    result = await controller.update_certificates_database()
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.message)
    
    return result