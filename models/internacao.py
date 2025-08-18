from sqlalchemy import (
    Column, Integer, ForeignKey,
    DateTime, Text, func
)
from sqlalchemy.orm import relationship
from database import Base

class Internacao(Base):
    __tablename__ = "internacoes"

    id             = Column(Integer, primary_key=True)
    paciente_id    = Column(Integer, ForeignKey("pacientes.id"), index=True, nullable=False)
    leito_id       = Column(Integer, ForeignKey("leitos.id"),   index=True, nullable=False)
    data_entrada   = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    data_alta      = Column(DateTime(timezone=True), nullable=True, index=True)
    motivo         = Column(Text, nullable=False)

    paciente       = relationship("Paciente", back_populates="internacoes")
    leito          = relationship("Leito",    back_populates="internacoes")