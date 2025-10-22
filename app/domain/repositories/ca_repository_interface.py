from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.approve_certificate import ApproveCertificate

class CARepositoryInterface(ABC):

    @abstractmethod
    async def get_certificate(self, registro_ca: str) -> Optional[ApproveCertificate]:
        pass

    @abstractmethod
    async def update_base_certificate(self) -> bool:
        pass
