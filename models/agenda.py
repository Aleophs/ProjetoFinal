from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class AgendaMedica(Base):
    __tablename__ = "agenda_medica"

    id             = Column(Integer, primary_key=True)
    profissional_id= Column(Integer, ForeignKey("profissionais.id"), index=True)
    data_hora      = Column(DateTime(timezone=True), index=True)
    disponivel     = Column(Boolean, server_default="true", nullable=False)

    profissional   = relationship("Profissional", back_populates="agendas")