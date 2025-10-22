from app.interface.dtos.certificate_dto import ApiResponse, CertificateResponse
from app.domain.entities.approve_certificate import ApproveCertificate


class CertificatePresenter:
    """Apresentador simplificado para certificados"""
    
    def present_certificate(self, certificate: ApproveCertificate) -> ApiResponse:
        """Apresenta um certificado"""
        if certificate is None:
            return ApiResponse(
                success=False,
                message="Certificado não encontrado",
                data=None
            )
        
        return ApiResponse(
            success=True,
            message="Certificado encontrado",
            data=CertificateResponse(
                registro_ca=certificate.registro_ca,
                data_validade=certificate.data_validade,
                situacao=certificate.situacao
            )
        )
    
    def present_error(self, message: str) -> ApiResponse:
        """Apresenta erro"""
        return ApiResponse(
            success=False,
            message=message,
            data=None
        )
    
    def present_update_result(self, success: bool, message: str = None) -> ApiResponse:
        """Apresenta resultado de atualização"""
        return ApiResponse(
            success=success,
            message=message or ("Atualização realizada" if success else "Falha na atualização"),
            data=None
        )