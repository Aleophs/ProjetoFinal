from sqlalchemy import (
    Column, Integer, String, Enum,
    DateTime, func
)
from sqlalchemy.orm import relationship
from database import Base
import enum

class PerfilEnum(str, enum.Enum):
    administrador = "Administrador"
    profissional  = "Profissional"
    paciente      = "Paciente"

class Usuario(Base):
    __tablename__ = "usuarios"

    id           = Column(Integer, primary_key=True)
    nome         = Column(String(100), nullable=False, index=True)
    email        = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash   = Column(String(255), nullable=False)
    perfil       = Column(
                       Enum(PerfilEnum),
                       nullable=False,
                       server_default=PerfilEnum.paciente.value
                   )
    criado_em    = Column(
                       DateTime(timezone=True),
                       server_default=func.now(),
                       nullable=False,
                       index=True
                   )

    # Relacionamento com logs de auditoria
    logs_auditoria = relationship(
        "LogAuditoria",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )