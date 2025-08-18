from sqlalchemy import (
    Column, Integer, ForeignKey, Text,
    DateTime, func
)
from sqlalchemy.orm import relationship
from database import Base

class EvolucaoClinica(Base):
    __tablename__ = "evolucoes_clinicas"

    id               = Column(Integer, primary_key=True)
    paciente_id      = Column(Integer, ForeignKey("pacientes.id"), index=True, nullable=False)
    profissional_id  = Column(Integer, ForeignKey("profissionais.id"), index=True, nullable=False)
    data_registro    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    anotacoes        = Column(Text, nullable=False)

    paciente         = relationship("Paciente", back_populates="evolucoes_clinicas")
    profissional     = relationship("Profissional", back_populates="evolucoes_clinicas")