from app.interface.dtos.certificate_dto import ApiResponse
from app.interface.presenters.certificate_presenter import CertificatePresenter
from app.application.use_cases.get_certificate_use_case import GetCertificateUseCase
from app.application.use_cases.update_certificates_use_case import UpdateCertificatesUseCase


class CertificateController:
    """Controller simplificado para certificados"""
    
    def __init__(
        self,
        get_certificate_use_case: GetCertificateUseCase,
        update_certificates_use_case: UpdateCertificatesUseCase,
        presenter: CertificatePresenter
    ):
        self.get_certificate_use_case = get_certificate_use_case
        self.update_certificates_use_case = update_certificates_use_case
        self.presenter = presenter
    
    async def get_certificate(self, registro_ca: str) -> ApiResponse:
        """Busca um certificado por registro CA"""
        try:
            if not registro_ca or not registro_ca.strip():
                return self.presenter.present_error("Registro CA é obrigatório")
            
            certificate = await self.get_certificate_use_case.execute(registro_ca.strip())
            return self.presenter.present_certificate(certificate)
            
        except Exception as e:
            return self.presenter.present_error(f"Erro interno: {str(e)}")
        
    async def update_certificates_database(self) -> ApiResponse:
        """Atualiza a base de dados de certificados"""
        try:
            success = await self.update_certificates_use_case.execute()
            return self.presenter.present_update_result(success)
            
        except Exception as e:
            return self.presenter.present_error(f"Erro ao atualizar: {str(e)}")