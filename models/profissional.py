from sqlalchemy import (
    Column, Integer, String
)
from sqlalchemy.orm import relationship
from database import Base

class Profissional(Base):
    __tablename__ = "profissionais"

    id                = Column(Integer, primary_key=True)
    nome              = Column(String(100), nullable=False)
    email             = Column(String(150), unique=True, nullable=False, index=True)
    especialidade     = Column(String(100), nullable=False, index=True)
    registro_conselho = Column(String(50), unique=True, nullable=False, index=True)

    evolucoes_clinicas = relationship(
        "EvolucaoClinica",
        back_populates="profissional",
        cascade="all, delete-orphan"
    )
    consultas = relationship(
        "Consulta",
        back_populates="profissional",
        cascade="all, delete-orphan"
    )
    prescricoes = relationship(
        "Prescricao",
        back_populates="profissional",
        cascade="all, delete-orphan"
    )
    agenda_medica = relationship(
        "AgendaMedica",
        back_populates="profissional",
        cascade="all, delete-orphan"
    )
    internacoes = relationship(
        "Internacao",
        back_populates="profissional",
        cascade="all, delete-orphan"
    )
    telemedicinas = relationship(
        "ConsultaTelemedicina",
        back_populates="profissional",
        cascade="all, delete-orphan"
    )
    agendas = relationship(
        "AgendaMedica",
        back_populates="profissional",
        cascade="all, delete-orphan",
        overlaps="agenda_medica"
    )
