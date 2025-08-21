from sqlalchemy import (
    Column, Integer, String,
    DateTime, Text, ForeignKey, func
)
from sqlalchemy.orm import relationship
from database import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id               = Column(Integer, primary_key=True)
    nome             = Column(String(100), nullable=False)
    email            = Column(String(150), unique=True, nullable=False, index=True)
    telefone         = Column(String(20), nullable=True)
    data_nascimento  = Column(DateTime(timezone=True), nullable=True, index=True)

    evolucoes_clinicas = relationship(
        "EvolucaoClinica",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
    internacoes = relationship(
        "Internacao",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
    historicos_clinicos = relationship(
        "HistoricoClinico",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
    prescricoes = relationship(
        "Prescricao",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
    telemedicinas = relationship(
        "ConsultaTelemedicina",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
    consultas             = relationship(
        "Consulta",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )


class HistoricoClinico(Base):
    __tablename__ = "historicos_clinicos"

    id             = Column(Integer, primary_key=True)
    paciente_id    = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    data_registro  = Column(
                      DateTime(timezone=True),
                      server_default=func.now(),
                      nullable=False,
                      index=True
                    )
    descricao      = Column(Text, nullable=False)
    profissional   = Column(String(100), nullable=False)

    paciente       = relationship("Paciente", back_populates="historicos_clinicos")