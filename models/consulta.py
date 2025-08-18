from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SqEnum,
)
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum

class StatusConsulta(PyEnum):
    Agendada   = "Agendada"
    Realizada  = "Realizada"
    Cancelada  = "Cancelada"

class Consulta(Base):
    __tablename__ = "consultas"

    id              = Column(Integer, primary_key=True)
    paciente_id     = Column(Integer, ForeignKey("pacientes.id"), index=True)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), index=True)
    data_hora       = Column(DateTime(timezone=True), index=True)
    especialidade   = Column(String(100), index=True)
    status          = Column(SqEnum(StatusConsulta), server_default="Agendada", nullable=False)

    paciente        = relationship("Paciente", back_populates="consultas")
    profissional    = relationship("Profissional", back_populates="consultas")