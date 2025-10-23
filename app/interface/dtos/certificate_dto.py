from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class CertificateResponse(BaseModel):
    """Resposta de certificado"""

    registro_ca: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Número do registro CA (apenas dígitos)"
    )
    data_validade: str = Field(
        ...,
        description="Data de validade do certificado (formato YYYY-MM-DD)"
    )
    situacao: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Situação atual do certificado (ex: Válido, Vencido)"
    )

    # Normaliza e valida a data automaticamente
    @field_validator("data_validade", mode="before")
    @classmethod
    def normalize_date(cls, value):
        if isinstance(value, str):
            value = value.strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    parsed = datetime.strptime(value, fmt)
                    return parsed.strftime("%Y-%m-%d")  # padroniza para ISO
                except ValueError:
                    continue
        raise ValueError("data_validade deve estar em um formato válido (YYYY-MM-DD ou DD/MM/YYYY)")

    # ✅ Normaliza e valida a situação
    @field_validator("situacao", mode="before")
    @classmethod
    def normalize_situacao(cls, value):
        if not isinstance(value, str):
            raise ValueError("situacao deve ser uma string")

        valor_normalizado = value.strip().capitalize()

        # Substituir variações comuns (sem acento, maiúsculas etc)
        mapa_valores = {
            "valido": "Válido",
            "válido": "Válido",
            "vencido": "Vencido",
            "cancelado": "Cancelado",
            "em analise": "Em análise",
            "em análise": "Em análise"
        }

        chave = valor_normalizado.lower().replace("á", "a").replace("í", "i").replace("ç", "c")
        if chave in mapa_valores:
            return mapa_valores[chave]

        raise ValueError(f"situacao deve ser um dos valores válidos: {list(mapa_valores.values())}")

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    """Resposta padrão da API"""

    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., min_length=3, description="Mensagem de status da operação")
    data: Optional[CertificateResponse] = Field(
        None,
        description="Dados do certificado, se aplicável"
    )

    @field_validator("data")
    @classmethod
    def validate_data_consistency(cls, value, info):
        # Em Pydantic v2, acessa-se o campo 'success' via info.data
        success = info.data.get("success") if info.data else None
        if success is False and value is not None:
            raise ValueError("Se success=False, data deve ser None")
        return value
