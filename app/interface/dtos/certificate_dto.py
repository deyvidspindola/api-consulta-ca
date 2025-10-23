from pydantic import BaseModel, Field
from typing import Optional


class CertificateRequest(BaseModel):
    """Requisição para buscar certificado por CA"""
    registro_ca: str = Field(
        ...,
        title="Registro CA",
        description="Número do registro do Certificado de Aprovação",
        example="12345",
        min_length=1
    )


class CertificateResponse(BaseModel):
    """Resposta de certificado"""
    registro_ca: str
    data_validade: str
    situacao: str
    
    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    """Resposta padrão da API"""
    success: bool
    message: str
    data: Optional[CertificateResponse] = None