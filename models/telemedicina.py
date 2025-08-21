from sqlalchemy import (
    Column, Integer, String,
    DateTime, Text, ForeignKey,
    func, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base

class ConsultaTelemedicina(Base):
    __tablename__ = "consultas_telemedicina"
    __table_args__ = (
        UniqueConstraint("link_video", name="uq_telemedicina_link"),
    )

    id               = Column(Integer, primary_key=True)
    paciente_id      = Column(Integer, ForeignKey("pacientes.id"), index=True, nullable=False)
    profissional_id  = Column(Integer, ForeignKey("profissionais.id"), index=True, nullable=False)
    data_hora        = Column(
                          DateTime(timezone=True),
                          server_default=func.now(),
                          nullable=False,
                          index=True
                      )
    link_video       = Column(String(200), nullable=False, index=True)
    observacoes      = Column(Text, nullable=True)

    paciente         = relationship("Paciente", back_populates="telemedicinas")
    profissional     = relationship("Profissional", back_populates="telemedicinas")