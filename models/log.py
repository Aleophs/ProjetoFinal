from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id            = Column(Integer, primary_key=True, index=True)
    usuario_email = Column(String(150), nullable=False, index=True)
    perfil        = Column(String(50), nullable=True,  index=True)
    metodo        = Column(String(10), nullable=False, index=True)
    endpoint      = Column(String(200), nullable=False, index=True)
    descricao     = Column(Text,      nullable=True)
    timestamp     = Column(
                      DateTime(timezone=True),
                      server_default=func.now(),
                      nullable=False,
                      index=True
                   )
    usuario_id    = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    usuario       = relationship("Usuario", back_populates="logs_auditoria")