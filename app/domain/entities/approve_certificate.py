
from dataclasses import dataclass

@dataclass
class ApproveCertificate:

    registro_ca: str
    data_validade: str
    situacao: str

    def approve(self):
        self.situacao = "Aprovado"

    def to_dict(self):
        return {
            "registro_ca": self.registro_ca,
            "data_validade": self.data_validade,
            "situacao": self.situacao
        }