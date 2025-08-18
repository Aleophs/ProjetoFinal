from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    func
)
from sqlalchemy.orm import relationship
from database import Base

class Prescricao(Base):
    __tablename__ = "prescricoes"

    id               = Column(Integer, primary_key=True)
    paciente_id      = Column(Integer, ForeignKey("pacientes.id"), index=True, nullable=False)
    profissional_id  = Column(Integer, ForeignKey("profissionais.id"), index=True, nullable=False)
    data_prescricao  = Column(
                          DateTime(timezone=True),
                          server_default=func.now(),
                          nullable=False,
                          index=True
                       )
    medicamento      = Column(String(100), index=True, nullable=False)
    posologia        = Column(Text, nullable=False)

    paciente         = relationship("PacienteModel", back_populates="prescricoes")
    profissional     = relationship("Profissional", back_populates="prescricoes")