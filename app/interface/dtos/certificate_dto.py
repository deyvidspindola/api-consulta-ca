from pydantic import BaseModel
from typing import Optional


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